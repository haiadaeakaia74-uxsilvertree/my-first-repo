#!/usr/bin/env python3
"""Validate x-post-log.md before X auto posting.

This does not send anything. It checks that the schedule is parseable, dates
are unique, referenced images exist, and there is a future post available.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = ROOT / "x-post-log.md"
POSTED_FILE = ROOT / "ops" / "sns" / "posted-dates.txt"


def parse_date(date_str: str) -> Optional[datetime]:
    match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{1,2}):(\d{2})", date_str)
    if not match:
        return None
    return datetime(
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        int(match.group(4)),
        int(match.group(5)),
    )


def parse_entries(content: str) -> list[dict]:
    pattern = re.compile(
        r"^## (?P<date>.+?)\n(?P<body>.*?)(?=^---\s*$\n|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    entries = []
    for match in pattern.finditer(content):
        body = match.group("body")
        text_match = re.search(r"^\*\*投稿文：\*\*\n(?P<text>.*?)(?=\n---\s*$|\Z)", body, re.MULTILINE | re.DOTALL)
        theme_match = re.search(r"^\*\*テーマ：\*\*\s*(.+)$", body, re.MULTILINE)
        image_match = re.search(r"^\*\*画像：\*\*\s*(.+)$", body, re.MULTILINE)
        if not text_match:
            continue
        entries.append(
            {
                "date": match.group("date").strip(),
                "datetime": parse_date(match.group("date").strip()),
                "theme": theme_match.group(1).strip() if theme_match else "",
                "image": image_match.group(1).strip() if image_match else None,
                "text": text_match.group("text").strip(),
            }
        )
    return entries


def posted_dates() -> set[str]:
    if not POSTED_FILE.exists():
        return set()
    return {line.strip() for line in POSTED_FILE.read_text(encoding="utf-8").splitlines() if line.strip()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Check X posting schedule")
    parser.add_argument("--require-future", action="store_true", help="Fail if no unposted future entries exist")
    args = parser.parse_args()

    content = LOG_FILE.read_text(encoding="utf-8")
    entries = parse_entries(content)
    posted = posted_dates()
    errors: list[str] = []
    warnings: list[str] = []

    seen: set[str] = set()
    now = datetime.now()
    future_unposted = 0

    for entry in entries:
        date = entry["date"]
        dt = entry["datetime"]
        if date in seen:
            errors.append(f"重複日時: {date}")
        seen.add(date)

        if dt is None:
            warnings.append(f"日時を解析できません: {date}")
        elif dt >= now and date not in posted:
            future_unposted += 1

        image = entry["image"]
        if image and image.lower() not in {"なし", "none", "daily"}:
            image_path = ROOT / image
            if not image_path.exists():
                errors.append(f"画像ファイルなし: {date} -> {image}")

        if not entry["text"]:
            errors.append(f"投稿文が空です: {date}")

    if args.require_future and future_unposted == 0:
        errors.append("未来の未投稿エントリがありません")

    print(f"X投稿チェック: {len(entries)}件 / 未来の未投稿 {future_unposted}件")
    for warning in warnings:
        print(f"警告: {warning}")
    for error in errors:
        print(f"エラー: {error}")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
