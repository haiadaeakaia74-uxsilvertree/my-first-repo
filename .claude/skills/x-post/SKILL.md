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

## 投稿予定を修正した後の必須反映

`x-post-log.md` の本文、テーマ、画像指定、ハッシュタグを修正した場合は、ローカル編集だけで完了にしない。
自動投稿は GitHub の `main` を読むため、変更後は必ず次まで行う。

1. 修正対象の差分を確認する。
2. 関係ない未整理変更を混ぜず、投稿に必要なファイルだけをコミットする。
3. GitHub の `main` へ push する。
4. `origin/main:x-post-log.md` を読み直し、最新本文が入っていることを確認する。
5. ユーザーには「ローカル修正済み」ではなく「GitHub反映確認済み」まで報告する。

画像付き投稿では、画像ファイルも `origin/main` に存在することを確認する。
