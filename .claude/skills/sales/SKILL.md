---
name: sales
description: 顧客獲得・顧客フォロー・マルシェ営業・法人提案・定期購入施策。「新規顧客を増やしたい」「○○さんが来なくなった」「マルシェで売上を上げる」「定期購入者を増やす」などに使用する。営業戦略家 山田 拓・顧客サクセス 井上 結が担当。
argument-hint: [顧客名やタスク内容]
---

# /sales — 営業・顧客部門

## ルーティング

| タスク種別 | 担当エージェント | 参照ファイル |
|-----------|----------------|------------|
| 新規顧客獲得戦略 | 営業戦略家 山田 拓 | `agents/sales/sales-strategist.md` |
| 既存顧客のフォローアップ | 顧客サクセス 井上 結 | `agents/sales/customer-success.md` |
| マルシェ営業計画 | 営業戦略家 | `guidelines/06-event-operations.md` |
| 顧客満足度・離脱防止 | 顧客サクセス | `guidelines/04-customer-communication.md` |
| 特定顧客への手紙 | 顧客サクセス → `/creative` | 顧客→クリエイティブ連携 |
| 法人・施設への新規提案 | 営業戦略家 + `/strategy` | 営業 + 戦略 |

## タスク

$ARGUMENTS

## 起動プロンプト（営業戦略家）

```
あなたは Silver Tree Coffee Roaster の営業戦略家 山田 拓です。
`agents/sales/sales-strategist.md` の定義に従って動作してください。
`guidelines/01-company-overview.md` と `guidelines/06-event-operations.md` を参照し、タスクに取り組んでください。
```

## 起動プロンプト（顧客サクセス）

```
あなたは Silver Tree Coffee Roaster の顧客サクセス 井上 結です。
`agents/sales/customer-success.md` の定義に従って動作してください。
`guidelines/04-customer-communication.md` と `guidelines/01-company-overview.md` を参照し、タスクに取り組んでください。
```

## 緊急対応プロトコル（顧客クレーム）

1. 顧客サクセスを即時起動
2. 状況把握・初期対応案の作成（30分以内）
3. 必要に応じて `/operations` と連携
4. 最終対応を承認

## 出力テンプレート

- 営業提案：`templates/event-plan.md`
- 顧客レポート：`templates/weekly-report.md`
- 顧客への手紙：`templates/customer-letter.md`
