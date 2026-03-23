"""
x_poster.py - X（Twitter）自動投稿スクリプト

x-post-log.md から未投稿の投稿文を読み取り、X に自動投稿します。
投稿済みの記録は .env ファイルの POSTED_DATES に保存されます。

使い方:
    python x_poster.py          # 未投稿をすべて投稿
    python x_poster.py --dry-run  # 投稿せずに内容を確認のみ
    python x_poster.py --list     # 投稿済み/未投稿の一覧を表示
"""

import argparse
import re
import sys
from pathlib import Path

import tweepy
from dotenv import dotenv_values, set_key

ENV_FILE = Path(".env")
LOG_FILE = Path("x-post-log.md")


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


def parse_log_file(log_path: Path) -> list[dict]:
    """
    x-post-log.md をパースして投稿エントリのリストを返す。
    各エントリは {"date": str, "theme": str, "text": str} の辞書。
    """
    if not log_path.exists():
        print(f"エラー: {log_path} が見つかりません。")
        sys.exit(1)

    content = log_path.read_text(encoding="utf-8")

    # ## 日付 ブロックで分割（--- で終わる）
    pattern = re.compile(
        r"^## (.+?)\n"          # ## 日付
        r".*?\*\*テーマ：\*\* (.+?)\n"  # **テーマ：** テーマ
        r"\*\*投稿文：\*\*\n"   # **投稿文：**
        r"(.*?)"                 # 投稿本文
        r"(?:^---$|\Z)",         # --- または EOF
        re.MULTILINE | re.DOTALL,
    )

    entries = []
    for match in pattern.finditer(content):
        date = match.group(1).strip()
        theme = match.group(2).strip()
        text = match.group(3).strip()
        if text:
            entries.append({"date": date, "theme": theme, "text": text})

    return entries


def get_posted_dates(config: dict) -> set[str]:
    raw = config.get("POSTED_DATES", "") or ""
    return {d.strip() for d in raw.split(",") if d.strip()}


def save_posted_date(date: str) -> None:
    config = dotenv_values(ENV_FILE)
    posted = get_posted_dates(config)
    posted.add(date)
    set_key(ENV_FILE, "POSTED_DATES", ",".join(sorted(posted)))


def post_tweet(client: tweepy.Client, text: str, dry_run: bool) -> bool:
    if dry_run:
        print("  [DRY-RUN] 投稿はスキップされました。")
        return True

    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        print(f"  投稿成功: https://x.com/i/web/status/{tweet_id}")
        return True
    except tweepy.TweepyException as e:
        print(f"  投稿失敗: {e}")
        return False


def cmd_list(entries: list[dict], posted_dates: set[str]) -> None:
    print(f"{'状態':<6} {'日付':<20} テーマ")
    print("-" * 60)
    for entry in entries:
        status = "投稿済" if entry["date"] in posted_dates else "未投稿"
        print(f"{status:<6} {entry['date']:<20} {entry['theme']}")
    print()
    print(f"合計 {len(entries)} 件 / 未投稿 {sum(1 for e in entries if e['date'] not in posted_dates)} 件")


def cmd_post(entries: list[dict], posted_dates: set[str], client: tweepy.Client, dry_run: bool) -> None:
    pending = [e for e in entries if e["date"] not in posted_dates]

    if not pending:
        print("未投稿の記事はありません。")
        return

    print(f"{len(pending)} 件の未投稿記事を処理します。\n")

    for entry in pending:
        print(f"【{entry['date']}】{entry['theme']}")
        print("-" * 40)
        print(entry["text"])
        print("-" * 40)

        success = post_tweet(client, entry["text"], dry_run)
        if success and not dry_run:
            save_posted_date(entry["date"])

        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="X（Twitter）自動投稿スクリプト")
    parser.add_argument("--dry-run", action="store_true", help="投稿せずに内容を確認のみ")
    parser.add_argument("--list", action="store_true", help="投稿済み/未投稿の一覧を表示")
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

    cmd_post(entries, posted_dates, client, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
