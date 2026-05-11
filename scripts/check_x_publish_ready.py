#!/usr/bin/env python3
"""Check whether X post edits are ready for GitHub Actions.

This catches the failure mode where local X schedule edits exist but have not
been pushed, so the scheduled GitHub Action posts older copy.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WATCHED_PATHS = [
    "x-post-log.md",
    "images/x",
    ".claude/skills/x-design-note-post",
    "ops/handoff/2026-05-09.md",
]


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> int:
    errors: list[str] = []

    schedule = run([sys.executable, "scripts/check_x_schedule.py", "--require-future"])
    print(schedule.stdout, end="")
    if schedule.returncode != 0:
        errors.append("X投稿スケジュールの検証に失敗しています。")

    status = run(["git", "status", "--porcelain", "--", *WATCHED_PATHS])
    if status.stdout.strip():
        errors.append("X投稿関連ファイルに未コミット変更があります。")
        print(status.stdout, end="")

    fetch = run(["git", "fetch", "origin", "main"])
    if fetch.returncode != 0:
        errors.append("origin/main を確認できません。ネットワークまたは認証を確認してください。")
        print(fetch.stdout, end="")
    else:
        ahead = run(["git", "rev-list", "--count", "origin/main..HEAD"])
        behind = run(["git", "rev-list", "--count", "HEAD..origin/main"])
        ahead_count = int((ahead.stdout or "0").strip())
        behind_count = int((behind.stdout or "0").strip())
        if behind_count:
            errors.append(f"GitHub側に未取得の更新があります: behind {behind_count}件。先に取り込んでください。")
        if ahead_count:
            errors.append(f"ローカルの変更がGitHub未反映です: ahead {ahead_count}件。pushが必要です。")

    if errors:
        print("\nX投稿公開前チェック: NG")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nX投稿公開前チェック: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
