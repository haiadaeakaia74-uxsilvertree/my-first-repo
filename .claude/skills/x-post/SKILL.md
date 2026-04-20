---
name: x-post
description: X（Twitter）への投稿を実行する。投稿文の作成は /marketing を使用し、実際の投稿実行にこのスキルを使う。
disable-model-invocation: true
argument-hint: [投稿テーマ or 投稿文]
allowed-tools: Bash(python *)
---

# /x-post — X 投稿実行スキル

**副作用のある操作のため、必ずユーザーが明示的に呼び出すこと。Claudeは自動実行しない。**

## 処理フロー

1. 投稿文の確認（引数またはテンプレートから）
2. `x_poster.py` を実行して X に投稿
3. `x-post-log.md` に記録
4. 投稿結果を報告

## タスク

投稿テーマ・内容：$ARGUMENTS

投稿文が未作成の場合：`/marketing $ARGUMENTS` で先に投稿文を作成し、承認を得てから本スキルを呼び出すこと。

## 実行コマンド

```bash
python x_poster.py
```

## 注意事項

- 投稿前に必ず内容を確認・承認する
- `guidelines/05-sns-operations.md` の運用ルールに従う
- 投稿後は `ops/sns/posted-dates.txt` と `x-post-log.md` を更新する
- 画像を添付する場合は `images/` ディレクトリから選択する
