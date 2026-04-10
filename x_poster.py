"""
x_poster.py - X（Twitter）自動投稿スクリプト

x-post-log.md から投稿文を読み取り、X に自動投稿します。
画像フィールドがある場合は画像付きで投稿します。
投稿済みの記録は ops/sns/posted-dates.txt に保存されます。

使い方:
    python x_poster.py --scheduled   # 現在時刻に対応する1件だけ投稿（自動化用）
    python x_poster.py --dry-run     # 投稿せずに内容を確認のみ
    python x_poster.py --list        # 投稿済み/未投稿/予定の一覧を表示
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import tweepy
from dotenv import dotenv_values

ENV_FILE = Path(".env")
LOG_FILE = Path("x-post-log.md")
POSTED_FILE = Path("ops/sns/posted-dates.txt")

SCHEDULED_WINDOW_MINUTES = 240  # GitHub Actions cron は最大2〜3時間遅延することがある


def load_config() -> dict:
    config = {}

    if ENV_FILE.exists():
        config = dict(dotenv_values(ENV_FILE))

    # 環境変数で上書き（GitHub Actions では Secrets がここに入る）
    for key in ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET", "BEARER_TOKEN"]:
        if os.environ.get(key):
            config[key] = os.environ[key]

    required_keys = ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]
    missing = [k for k in required_keys if not config.get(k) or "your_" in config.get(k, "")]
    if missing:
        print(f"エラー: 以下のキーが未設定です: {', '.join(missing)}")
        sys.exit(1)

    return config


def get_twitter_client(config: dict) -> tweepy.Client:
    return tweepy.Client(
        bearer_token=config.get("BEARER_TOKEN"),
        consumer_key=config["API_KEY"],
        consumer_secret=config["API_SECRET"],
        access_token=config["ACCESS_TOKEN"],
        access_token_secret=config["ACCESS_TOKEN_SECRET"],
    )


def get_v1_api(config: dict) -> tweepy.API:
    """画像アップロード用の v1.1 API クライアント。"""
    auth = tweepy.OAuth1UserHandler(
        consumer_key=config["API_KEY"],
        consumer_secret=config["API_SECRET"],
        access_token=config["ACCESS_TOKEN"],
        access_token_secret=config["ACCESS_TOKEN_SECRET"],
    )
    return tweepy.API(auth)


def parse_log_file(log_path: Path) -> list[dict]:
    """x-post-log.md をパースして全エントリを返す。"""
    if not log_path.exists():
        print(f"エラー: {log_path} が見つかりません。")
        sys.exit(1)

    content = log_path.read_text(encoding="utf-8")

    # HTMLコメントブロックを除去
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

    pattern = re.compile(
        r"^## (.+?)\n"
        r"(.*?)"
        r"\*\*投稿文：\*\*\n"
        r"(.*?)"
        r"(?:^---$|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    entries = []
    for match in pattern.finditer(content):
        date = match.group(1).strip()
        meta = match.group(2)
        text = match.group(3).strip()
        if not text:
            continue

        # テーマを取得
        theme_m = re.search(r"\*\*テーマ：\*\* (.+)", meta)
        theme = theme_m.group(1).strip() if theme_m else ""

        # 画像パスを取得
        image_m = re.search(r"\*\*画像：\*\* (.+)", meta)
        image = image_m.group(1).strip() if image_m else None

        entries.append({
            "date": date,
            "theme": theme,
            "text": text,
            "image": image,
            "datetime": _parse_date(date),
        })

    entries.sort(key=lambda e: e["datetime"] or datetime.max)
    return entries


def _parse_date(date_str: str) -> datetime | None:
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{1,2}):(\d{2})", date_str)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                        int(m.group(4)), int(m.group(5)))
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def get_posted_dates() -> set[str]:
    if not POSTED_FILE.exists():
        return set()
    return {line.strip() for line in POSTED_FILE.read_text(encoding="utf-8").splitlines() if line.strip()}


def save_posted_date(date: str) -> None:
    posted = get_posted_dates()
    posted.add(date)
    POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    POSTED_FILE.write_text("\n".join(sorted(posted)) + "\n", encoding="utf-8")


def resolve_image(image: str | None, entry_dt: datetime | None) -> str | None:
    """imageフィールドを実際のパスに解決する。
    'daily' の場合は images/daily/YYYY-MM-DD.{jpg,jpeg,png} を自動検索。
    """
    if image is None:
        return None
    if image.strip().lower() in ("daily", "なし", "none", ""):
        if image.strip().lower() in ("なし", "none", ""):
            return None
        # daily モード：投稿日付で images/daily/ を検索
        if entry_dt is None:
            return None
        date_str = entry_dt.strftime("%Y-%m-%d")
        for ext in ["jpg", "jpeg", "png"]:
            path = Path(f"images/daily/{date_str}.{ext}")
            if path.exists():
                print(f"  [daily] 写真を使用: {path}")
                return str(path)
        print(f"  [daily] {date_str} の写真が見つかりません。テキストのみで投稿します。")
        return None
    return image



    if dry_run:
        if image:
            print(f"  [DRY-RUN] 画像あり: {image}")
        print("  [DRY-RUN] 投稿はスキップされました。")
        return True

    media_ids = None

    if image:
        image_path = Path(image)
        print(f"  [DEBUG] 作業ディレクトリ: {Path.cwd()}")
        print(f"  [DEBUG] 画像パス: {image_path} / 絶対パス: {image_path.resolve()}")
        print(f"  [DEBUG] ファイル存在: {image_path.exists()}")
        if image_path.exists():
            print(f"  [DEBUG] ファイルサイズ: {image_path.stat().st_size} bytes")
            try:
                media = api.media_upload(filename=str(image_path))
                media_ids = [media.media_id]
                print(f"  画像アップロード完了: {image} (media_id={media.media_id})")
            except Exception as e:
                print(f"  警告: 画像アップロード失敗（{type(e).__name__}: {e}）。テキストのみで投稿します。")
        else:
            print(f"  警告: 画像ファイルが見つかりません（{image}）。テキストのみで投稿します。")

    try:
        response = client.create_tweet(text=text, media_ids=media_ids)
        tweet_id = response.data["id"]
        print(f"  投稿成功: https://x.com/i/web/status/{tweet_id}")
        return True
    except tweepy.TweepyException as e:
        print(f"  投稿失敗: {e}")
        if hasattr(e, "api_errors") and e.api_errors:
            for err in e.api_errors:
                print(f"  [API ERROR] code={err.get('code')} message={err.get('message')}")
        if hasattr(e, "response") and e.response is not None:
            print(f"  [RESPONSE] status={e.response.status_code} body={e.response.text[:300]}")
        return False


def cmd_scheduled(entries: list[dict], posted_dates: set[str], client: tweepy.Client, api: tweepy.API, dry_run: bool) -> None:
    """現在時刻に対応する1件だけ投稿する（GitHub Actions 自動実行用）。"""
    now = datetime.now()

    target = None
    for entry in entries:
        if entry["date"] in posted_dates:
            continue
        dt = entry["datetime"]
        if dt is None:
            continue
        diff_minutes = (now - dt).total_seconds() / 60
        if 0 <= diff_minutes <= SCHEDULED_WINDOW_MINUTES:
            target = entry
            break

    if target is None:
        print(f"[{now.strftime('%Y-%m-%d %H:%M')}] 対応する投稿が見つかりません（予定時刻を過ぎた{SCHEDULED_WINDOW_MINUTES}分以内）。")
        return

    print(f"[{now.strftime('%Y-%m-%d %H:%M')}] 投稿します: 【{target['date']}】{target['theme']}")
    if target["image"]:
        print(f"  画像: {target['image']}")
    print("-" * 40)
    print(target["text"])
    print("-" * 40)

    resolved_image = resolve_image(target["image"], target["datetime"])
    success = post_tweet(client, api, target["text"], resolved_image, dry_run)
    if success and not dry_run:
        save_posted_date(target["date"])


def cmd_list(entries: list[dict], posted_dates: set[str]) -> None:
    now = datetime.now()
    print(f"{'状態':<6} {'画像':<4} {'日付':<25} テーマ")
    print("-" * 75)
    for entry in entries:
        dt = entry["datetime"]
        if dt and dt > now:
            status = "予定"
        elif entry["date"] in posted_dates:
            status = "投稿済"
        else:
            status = "未投稿"
        img = "🖼" if entry["image"] else "  "
        print(f"{status:<6} {img:<4} {entry['date']:<25} {entry['theme']}")
    print()
    pending = [e for e in entries if e["date"] not in posted_dates and (e["datetime"] or datetime.max) <= now]
    print(f"合計 {len(entries)} 件 / 未投稿（当日以前）{len(pending)} 件")


def main() -> None:
    parser = argparse.ArgumentParser(description="X（Twitter）自動投稿スクリプト")
    parser.add_argument("--scheduled", action="store_true", help="現在時刻に対応する1件だけ投稿（自動化用）")
    parser.add_argument("--dry-run", action="store_true", help="投稿せずに内容を確認のみ")
    parser.add_argument("--list", action="store_true", help="投稿済み/未投稿/予定の一覧を表示")
    args = parser.parse_args()

    config = load_config()
    entries = parse_log_file(LOG_FILE)
    posted_dates = get_posted_dates()

    if args.list:
        cmd_list(entries, posted_dates)
        return

    client = get_twitter_client(config)
    api = get_v1_api(config)

    if args.dry_run:
        print("=== DRY-RUN モード（実際には投稿しません）===\n")

    if args.scheduled:
        cmd_scheduled(entries, posted_dates, client, api, dry_run=args.dry_run)
    else:
        now = datetime.now()
        pending = [
            e for e in entries
            if e["date"] not in posted_dates
            and (e["datetime"] or datetime.max) <= now
        ]
        if not pending:
            print("未投稿の記事はありません。")
            return
        print(f"{len(pending)} 件の未投稿記事を処理します。\n")
        for entry in pending:
            print(f"【{entry['date']}】{entry['theme']}")
            if entry["image"]:
                print(f"  画像: {entry['image']}")
            print("-" * 40)
            print(entry["text"])
            print("-" * 40)
            resolved_image = resolve_image(entry["image"], entry["datetime"])
            success = post_tweet(client, api, entry["text"], resolved_image, dry_run=args.dry_run)
            if success and not args.dry_run:
                save_posted_date(entry["date"])
            print()


if __name__ == "__main__":
    main()
