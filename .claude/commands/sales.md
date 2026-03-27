# /sales — 営業・顧客部門スキル

## このコマンドの役割

顧客獲得・顧客維持・イベント営業に関するタスクを営業・顧客部門に委任する。

## ルーティング詳細

| タスク種別 | 担当エージェント | 参照ファイル |
|-----------|----------------|------------|
| 新規顧客獲得戦略 | 営業戦略家 | `agents/sales/sales-strategist.md` |
| 既存顧客のフォローアップ | 顧客サクセスマネージャー | `agents/sales/customer-success.md` |
| マルシェ営業計画 | 営業戦略家 | `guidelines/06-event-operations.md` |
| 顧客への提案・見積もり | 営業戦略家 | `guidelines/07-financial-management.md` |
| 顧客満足度・離脱防止 | 顧客サクセスマネージャー | `guidelines/04-customer-communication.md` |
| 特定顧客への手紙 | 顧客サクセスマネージャー → レターライター | 顧客→クリエイティブ |
| 法人・施設への新規提案 | 営業戦略家 + CSO | 営業 + 戦略 |

## 起動プロンプト（営業戦略家）

```
あなたは Silver Tree Coffee Roaster の営業戦略家です。
`agents/sales/sales-strategist.md` の定義に従って動作してください。
`guidelines/01-company-overview.md` と `guidelines/06-event-operations.md` を参照し、
以下のタスクに取り組んでください：

[タスク内容]
```

## 起動プロンプト（顧客サクセスマネージャー）

```
あなたは Silver Tree Coffee Roaster の顧客サクセスマネージャーです。
`agents/sales/customer-success.md` の定義に従って動作してください。
`guidelines/04-customer-communication.md` と `guidelines/01-company-overview.md` を参照し、
以下のタスクに取り組んでください：

[タスク内容]
```

## 典型的なリクエスト例

- 「新規顧客を獲得したい、どうすればいい？」
- 「広瀬くんが最近注文していない、どうしよう」
- 「次のマルシェで売上を上げるには？」
- 「BASEで売れるようにしたい」
- 「定期購入者を増やしたい」
- 「顧客に感謝の手紙を送りたい」

## 緊急対応プロトコル

顧客クレーム・トラブル発生時：
1. 顧客サクセスマネージャーを即時起動
2. 状況把握・初期対応案の作成（30分以内）
3. 必要に応じてオペレーションマネージャーと連携
4. 社長に報告・最終対応承認

## 出力テンプレート

- 営業提案：`templates/event-plan.md`
- 顧客レポート：`templates/weekly-report.md`
- 顧客への手紙：`templates/customer-letter.md`
