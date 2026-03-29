"""
x_poster.py - X（Twitter）自動投稿スクリプト（時刻スケジュール対応版）

x-post-log.md から未投稿の投稿文を読み取り、X に自動投稿します。
スケジュール時刻が現在時刻以前の投稿のみ処理します。
投稿済みの記録は .env ファイルの POSTED_DATES に保存されます。
画像パスが指定されている場合は画像付きで投稿します。

使い方:
    python x_poster.py          # スケジュール済みの未投稿を投稿
    python x_poster.py --dry-run  # 投稿せずに内容を確認のみ
    python x_poster.py --list     # スケジュール一覧を表示

ログ書式（画像付き投稿の例）:
    ## 2026年4月1日 07:00
    **テーマ：** テーマ名
    **画像：** images/photo.jpg
    **投稿文：**
    投稿テキスト...

    ---

cron 設定例（毎日 朝7時・昼12時・夜20時に自動実行）:
    0 7,12,20 * * * cd /home/user/my-first-repo && python x_poster.py >> /tmp/x_poster.log 2>&1
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import tweepy
from dotenv import dotenv_values, set_key

ENV_FILE = Path(".env")
LOG_FILE = Path("x-post-log.md")
JST = ZoneInfo("Asia/Tokyo")


def load_config() -> dict:
    if not ENV_FILE.exists():
        print(f"エラー: {ENV_FILE} が見つかりません。")
        print(".env.template をコピーして .env を作成し、APIキーを設定してください。")
        sys.exit(1)

    config = dotenv_values(ENV_FILE)
    required_keys = ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]
    missing = [k for k in required_keys if not config.get(k) or "your_" in config.get(k, "")]
    if missing:
        print(f"エラー: .env に以下のキーが未設定です: {', '.join(missing)}")
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


def get_twitter_v1_api(config: dict) -> tweepy.API:
    """画像アップロード用 v1.1 API クライアント"""
    auth = tweepy.OAuth1UserHandler(
        config["API_KEY"],
        config["API_SECRET"],
        config["ACCESS_TOKEN"],
        config["ACCESS_TOKEN_SECRET"],
    )
    return tweepy.API(auth)


def parse_scheduled_datetime(date_str: str) -> Optional[datetime]:
    """
    '2026年3月30日 07:00' または '2026年2月25日' 形式をパース。
    時刻なしの場合は 00:00 として扱う（即時投稿可能）。
    """
    m = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{2}):(\d{2})", date_str)
    if m:
        y, mo, d, h, mi = map(int, m.groups())
        return datetime(y, mo, d, h, mi, tzinfo=JST)

    m = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
    if m:
        y, mo, d = map(int, m.groups())
        return datetime(y, mo, d, 0, 0, tzinfo=JST)

    return None


def parse_log_file(log_path: Path) -> list[dict]:
    """
    x-post-log.md をパースして投稿エントリのリストを返す。
    各エントリは {"date": str, "theme": str, "text": str, "scheduled_at": datetime} の辞書。
    """
    if not log_path.exists():
        print(f"エラー: {log_path} が見つかりません。")
        sys.exit(1)

    content = log_path.read_text(encoding="utf-8")

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
        meta_block = match.group(2)
        text = match.group(3).strip()

        theme_m = re.search(r"\*\*テーマ：\*\* (.+)", meta_block)
        theme = theme_m.group(1).strip() if theme_m else ""

        image_m = re.search(r"\*\*画像：\*\* (.+)", meta_block)
        image = image_m.group(1).strip() if image_m else None

        if text:
            entries.append({
                "date": date,
                "theme": theme,
                "text": text,
                "image": image,
                "scheduled_at": parse_scheduled_datetime(date),
            })

    return entries


def get_posted_dates(config: dict) -> set[str]:
    raw = config.get("POSTED_DATES", "") or ""
    return {d.strip() for d in raw.split(",") if d.strip()}


def save_posted_date(date: str) -> None:
    config = dotenv_values(ENV_FILE)
    posted = get_posted_dates(config)
    posted.add(date)
    set_key(ENV_FILE, "POSTED_DATES", ",".join(sorted(posted)))


def upload_image(v1_api: tweepy.API, image_path: str) -> Optional[int]:
    """画像をアップロードして media_id を返す"""
    path = Path(image_path)
    if not path.exists():
        print(f"  警告: 画像ファイルが見つかりません: {image_path}")
        return None
    try:
        media = v1_api.media_upload(filename=str(path))
        print(f"  画像アップロード成功: {image_path} (media_id={media.media_id})")
        return media.media_id
    except tweepy.TweepyException as e:
        print(f"  画像アップロード失敗: {e}")
        return None


def post_tweet(
    client: tweepy.Client,
    text: str,
    dry_run: bool,
    image_path: Optional[str] = None,
    v1_api: Optional[tweepy.API] = None,
) -> bool:
    if dry_run:
        if image_path:
            print(f"  [DRY-RUN] 画像: {image_path}")
        print("  [DRY-RUN] 投稿はスキップされました。")
        return True

    media_ids = None
    if image_path and v1_api:
        media_id = upload_image(v1_api, image_path)
        if media_id:
            media_ids = [media_id]

    try:
        response = client.create_tweet(text=text, media_ids=media_ids)
        tweet_id = response.data["id"]
        print(f"  投稿成功: https://x.com/i/web/status/{tweet_id}")
        return True
    except tweepy.TweepyException as e:
        print(f"  投稿失敗: {e}")
        return False


def cmd_list(entries: list[dict], posted_dates: set[str]) -> None:
    now = datetime.now(JST)
    print(f"{'状態':<6} {'スケジュール':<28} テーマ")
    print("-" * 75)
    for entry in entries:
        if entry["date"] in posted_dates:
            status = "投稿済"
        elif entry["scheduled_at"] and entry["scheduled_at"] > now:
            status = "待機中"
        else:
            status = "未投稿"
        print(f"{status:<6} {entry['date']:<28} {entry['theme']}")

    pending = sum(
        1 for e in entries
        if e["date"] not in posted_dates
        and (e["scheduled_at"] is None or e["scheduled_at"] <= now)
    )
    waiting = sum(
        1 for e in entries
        if e["date"] not in posted_dates
        and e["scheduled_at"] and e["scheduled_at"] > now
    )
    print()
    print(f"合計 {len(entries)} 件 / 投稿可能 {pending} 件 / 待機中 {waiting} 件")


def cmd_post(
    entries: list[dict],
    posted_dates: set[str],
    client: tweepy.Client,
    dry_run: bool,
    config: dict,
) -> None:
    now = datetime.now(JST)

    pending = [
        e for e in entries
        if e["date"] not in posted_dates
        and (e["scheduled_at"] is None or e["scheduled_at"] <= now)
    ]

    if not pending:
        print("投稿可能な未投稿記事はありません。")
        return

    print(f"{len(pending)} 件の投稿を処理します。\n")

    v1_api = get_twitter_v1_api(config)

    for entry in pending:
        print(f"【{entry['date']}】{entry['theme']}")
        if entry.get("image"):
            print(f"  📷 画像: {entry['image']}")
        print("-" * 40)
        print(entry["text"])
        print("-" * 40)

        success = post_tweet(
            client,
            entry["text"],
            dry_run,
            image_path=entry.get("image"),
            v1_api=v1_api,
        )
        if success and not dry_run:
            save_posted_date(entry["date"])

        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="X（Twitter）自動投稿スクリプト")
    parser.add_argument("--dry-run", action="store_true", help="投稿せずに内容を確認のみ")
    parser.add_argument("--list", action="store_true", help="スケジュール一覧を表示")
    args = parser.parse_args()

    config = load_config()
    entries = parse_log_file(LOG_FILE)
    posted_dates = get_posted_dates(config)

    if args.list:
        cmd_list(entries, posted_dates)
        return

    client = get_twitter_client(config)

    if args.dry_run:
        print("=== DRY-RUN モード（実際には投稿しません）===\n")

    cmd_post(entries, posted_dates, client, dry_run=args.dry_run, config=config)


if __name__ == "__main__":
    main()
