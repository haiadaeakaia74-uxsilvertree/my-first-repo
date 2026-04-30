# CODEX.md — Silver Tree Codex 運用メモ

## 基本方針

Codexは Silver Tree Coffee Roaster の運用補佐として、既存の `CLAUDE.md`、`.claude/skills/`、`guidelines/`、`ops/`、`reports/` の形式を引き継ぐ。

外部サービスへの投稿・送信・公開・購入・申請は、ユーザー確認後に行う。Codexが自動でX、Instagram、LINE、CAMPFIRE、BASE、メールへ投稿・送信しない。

## X運用

- X投稿はGitHub Actionsで自動継続する。
- `.github/workflows/x-post.yml` は30分ごとに起動し、`x_poster.py --scheduled` が投稿ウィンドウ内の未投稿エントリを1件投稿する。
- `workflow_dispatch` は手動確認・再実行用に残す。
- 投稿文は `x-post-log.md` に記録する。
- 投稿済み記録は `ops/sns/posted-dates.txt` に残す。
- Codexは投稿予定の作成、信憑性確認、画像生成、ログ整備を担当する。
- 自動投稿対象に入れる前に、本文・画像・投稿日時を確認する。
- X APIキーはGitHub Secretsで管理し、リポジトリやチャットに出さない。

## 投稿文からインフォグラフィック生成

X用インフォグラフィックは `scripts/generate_x_infographic.py` を使う。

### 信憑性確認ルール（必須）

コーヒー知識、抽出理論、焙煎、産地、健康・安全、数字を含む投稿からインフォグラフィックを作るときは、画像生成前に必ず信憑性を確認する。

- 数値、温度、時間、比率、産地情報、科学的説明は一次情報または信頼できる専門情報で確認する。
- 代表的な参照先は SCA、Coffee Science Foundation、論文、メーカー公式資料、既存の `guidelines/knowledge/`。
- 根拠が曖昧な場合は断定しない。必要なら「目安」「調整しやすい」「一般的には」に弱める。
- 既存投稿文に誤りが疑われる場合は、画像化する前に投稿文を修正する。
- 未確認のまま知識系インフォグラフィックを生成しない。
- 最終報告では、確認した根拠と修正有無を短く伝える。

基本コマンド:

```bash
python3 scripts/generate_x_infographic.py --date "2026年5月10日 07:00"
```

処理内容:

1. `x-post-log.md` から対象日時の投稿を読む。
2. 投稿テーマと本文からタイトル、サブタイトル、3〜4個のポイントを作る。
3. `images/x/YYYY-MM-DD_infographic-[slug].jpg` に保存する。
4. `x-post-log.md` の対象投稿に `**画像：**` 行を追加または更新する。

画像だけ作り、ログを更新しない場合:

```bash
python3 scripts/generate_x_infographic.py --date "2026年5月10日 07:00" --no-update
```

画像未設定の知識系投稿をまとめて生成する場合:

```bash
python3 scripts/generate_x_infographic.py --all-missing
```

GitHub Actions から手動実行する場合は、`Xインフォグラフィック生成` ワークフローを使う。日時を空欄にすると画像未設定の知識系投稿をまとめて生成し、日時を指定すると1件だけ生成する。

### 自動投稿前のチェック

自動投稿を継続するため、`x-post-log.md` に未来の投稿を入れる前に以下を確認する。

- 投稿日時がJSTで正しい。
- `ops/sns/posted-dates.txt` に同じ日時が入っていない。
- 画像付き投稿は画像ファイルが存在する。
- 知識系投稿は信憑性確認済み。
- CAMPFIRE、BASE、LINEなど外部リンクが必要な投稿はURLが確定している。

## 在庫・焙煎・財務

- 在庫は `.claude/skills/inventory/SKILL.md` の形式を維持する。
- 焙煎ログは `.claude/skills/roast-log/SKILL.md` の形式を維持する。
- 焙煎後処理は `.claude/skills/roast-inventory-sync/SKILL.md` の流れで、焙煎プロファイル、在庫、SNS案を連動させる。
- 財務は `.claude/skills/monthly-financial-summary/SKILL.md` の形式を維持する。

HTMLダッシュボード:

- 在庫: `ops/inventory/index.html`
- 焙煎: `roast-profiles/index.html`
- 財務: `reports/finance/dashboard.html`

## セキュリティ

- `.env` やAPIキーはコミットしない。
- GitHub Secrets、X API、BASE、CAMPFIRE、メール、決済情報はチャットに貼らない。
- 画像・投稿・CSVなどを外部へ送る前に、送信先と内容を確認する。
- 大きな変更は作業ブランチで行い、`main` への反映前に差分確認する。
