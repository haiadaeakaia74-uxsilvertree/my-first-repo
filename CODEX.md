# CODEX.md — Silver Tree Codex 運用メモ

## 基本方針

Codexは Silver Tree Coffee Roaster の運用補佐として、既存の `CLAUDE.md`、`.claude/skills/`、`guidelines/`、`ops/`、`reports/` の形式を引き継ぐ。

外部サービスへの投稿・送信・公開・購入・申請は、ユーザー確認後に行う。Codexが自動でX、Instagram、LINE、CAMPFIRE、BASE、メールへ投稿・送信しない。

## 現在方針（2026-05-01 以降）

Silver Tree Coffee Roaster / silvertree coffee の運用では、以下を最新方針として優先する。

- 手紙サービスは基本削除する。
- ギフト体験として「おみくじ」だけを残す。
- 梅・竹・松の商品階層は使わない。
- スペシャルティコーヒー専門へ寄せる。
- 古い「旅するコーヒー屋」「CAMPFIRE」「4分回復」文脈は、そのまま再利用しない。
- 過去ログに旧方針の投稿が残っていても、今後の新規投稿・画像・商品説明・ガイドラインでは現在方針を優先する。

詳細は `guidelines/current-brand-policy.md` を参照する。

## CAMPFIRE期間の優先方針（2026-05-02〜2026-06-11）

- Silver Tree Coffee Roaster の主軸は「旅するコーヒー屋」「CAMPFIREクラウドファンディング」「スペシャルティコーヒー」「自家焙煎」。
- 2026年5月1日はクラウドファンディング開始日。期間中の最優先目的はCAMPFIREリンクをX、Instagram、LINEで広めること。
- 2026年5月2日から2026年6月11日のクラウドファンディング終了日までは、SNS運用の最優先目的をCAMPFIRE拡散に置く。
- CAMPFIRE本公開URLは `https://camp-fire.jp/projects/944948`。
- 2026年5月1日時点で50,000円の支援、目標300,000円に対して16%。支援者名は出さず、感謝とシェア依頼に使う。
- この期間のX、Instagram、LINEは、通常投稿だけで終わらせない。旅するコーヒー屋の意義、進捗、リターン、応援依頼、シェア依頼、締切告知を継続して入れる。
- 「手紙屋サービス」「梅竹松」「未来手紙」は廃止済み。手紙はギフトセットのおみくじ要素としてのみ扱う。
- CAMPFIREや旅するコーヒー屋は期間中の現行施策として扱う。外す対象は、手紙サービスを主軸にする古い流れ。
- チャットで回答するときも、この主軸を同じ基準として扱う。

## X運用

- X投稿はGitHub Actionsで自動継続する。
- `.github/workflows/x-post.yml` は30分ごとに起動し、`x_poster.py --scheduled` が投稿ウィンドウ内の未投稿エントリを1件投稿する。
- `workflow_dispatch` は手動確認・再実行用に残す。
- 投稿文は `x-post-log.md` に記録する。
- 投稿済み記録は `ops/sns/posted-dates.txt` に残す。
- Codexは投稿予定の作成、信憑性確認、画像生成、ログ整備を担当する。
- 自動投稿対象に入れる前に、本文・画像・投稿日時を確認する。
- X APIキーはGitHub Secretsで管理し、リポジトリやチャットに出さない。
- `x-post-log.md` に旧方針の投稿が残っている場合でも、2026-05-01以降の新規投稿・修正投稿は現在方針に合わせる。

## 投稿文からインフォグラフィック生成

X用インフォグラフィックは `scripts/generate_x_infographic.py` を使う。
知識系の内容は、先に `.claude/skills/fact-check-infographic/SKILL.md` の手順で信憑性確認を行う。

### 信憑性確認ルール（必須）

コーヒー知識、抽出理論、焙煎、産地、健康・安全、数字を含む投稿からインフォグラフィックを作るときは、画像生成前に必ず信憑性を確認する。
知識系投稿は専門性と信頼を作るための投稿なので、未検証のままインフォグラフィック化・自動投稿しない。

- 数値、温度、時間、比率、産地情報、科学的説明は一次情報または信頼できる専門情報で確認する。
- 代表的な参照先は SCA、Coffee Science Foundation、論文、メーカー公式資料、既存の `guidelines/knowledge/`。
- 個人ブログ、生成AI回答、引用元不明のまとめ記事だけを根拠にしない。
- リサーチで根拠を確認し、主張ごとにOK / 修正 / NGを判定してから画像化する。
- 根拠が曖昧な場合は断定しない。必要なら「目安」「調整しやすい」「一般的には」に弱める。
- 既存投稿文に誤りが疑われる場合は、画像化する前に投稿文を修正する。
- 未確認のまま知識系インフォグラフィックを生成しない。
- ブランド表現は `guidelines/current-brand-policy.md` に合わせる。
- NGまたは未確認の知識系投稿は、インフォグラフィックを生成しない。自動投稿対象にも入れない。
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
- BASE、LINEなど外部リンクが必要な投稿はURLが確定している。
- CAMPFIRE期間中の投稿は `ops/sns/crowdfunding-campaign-policy-2026-05-02-06-11.md` に合わせる。
- 手紙サービス、梅竹松、4分回復、旅するコーヒー屋の文脈を惰性で使っていない。

ローカル確認:

```bash
python3 scripts/check_x_schedule.py
```

GitHub ActionsのX自動投稿でも、投稿前に同じチェックを実行する。

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
