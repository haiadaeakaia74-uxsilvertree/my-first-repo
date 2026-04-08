# /strategy — 戦略部門スキル

## このコマンドの役割

戦略・ビジョン・方向性・意思決定に関するタスクを CSO（戦略参謀）に委任する。

## ルーティング詳細

| タスク種別 | 担当エージェント | 参照ファイル |
|-----------|----------------|------------|
| 中長期ビジョンの策定・確認 | CSO | `agents/strategy/chief-strategy-officer.md` |
| 新規事業・チャネルの評価 | CSO → 財務マネージャー（数字）| 戦略 + 財務 |
| 競合・市場の分析 | CSO | `guidelines/01-company-overview.md` |
| 複数施策の優先順位決定 | CSO | `templates/strategy-report.md` |
| 経営課題の構造化 | CSO | `guidelines/01-company-overview.md` |

## 起動プロンプト

```
あなたは Silver Tree Coffee Roaster の CSO（戦略参謀）です。
`agents/strategy/chief-strategy-officer.md` の定義に従って動作してください。
`guidelines/01-company-overview.md` と `guidelines/02-brand-identity.md` を参照し、
以下のタスクに取り組んでください：

[タスク内容]
```

## 典型的なリクエスト例

- 「来年の事業の方向性を考えたい」
- 「マルシェとBASEとどちらに注力すべきか」
- 「法人販売に参入すべきか判断したい」
- 「今の課題を整理してほしい」
- 「やることが多くて優先順位がわからない」

## 複合タスク時の処理

戦略判断に数字が必要な場合：
1. CSOが戦略フレームを設計
2. 財務マネージャーに数字の試算を並列依頼
3. CSOが統合して社長に報告

戦略判断にブランド確認が必要な場合：
1. CSOが戦略案を作成
2. ブランドディレクターに整合性評価を依頼
3. 評価結果を統合して最終提案

## 出力テンプレート

`templates/strategy-report.md` を使用する。
