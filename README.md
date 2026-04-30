# my-first-repo
ここれは私のリポジトリです。

## Silver Tree 運用入口

- Codex運用ルール: `CODEX.md`
- 在庫ダッシュボード: `ops/inventory/index.html`
- 焙煎プロファイル: `roast-profiles/index.html`
- 財務ダッシュボード: `reports/finance/dashboard.html`
- X投稿ログ: `x-post-log.md`

## X運用

Xの定期自動投稿はGitHub Actionsで継続します。Codexでは投稿予定の作成、信憑性確認、インフォグラフィック生成、ログ整備を担当します。

知識系インフォグラフィックは、生成前に必ず信憑性を確認します。数値・温度・時間・科学的説明に誤りが疑われる場合は、投稿文を修正してから画像化します。

投稿文からX用インフォグラフィックを作る場合:

```bash
python3 scripts/generate_x_infographic.py --date "2026年5月10日 07:00"
```

画像未設定の知識系投稿をまとめて生成する場合:

```bash
python3 scripts/generate_x_infographic.py --all-missing
```
