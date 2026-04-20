---
name: marketing
description: SNS運用・コンテンツ戦略・コピーライティング・フォロワー施策。「投稿文を作りたい」「SNS戦略を立てたい」「コンテンツ計画」「フォロワーを増やす」「BASEの商品説明を改善」などに使用する。SNS戦略家 伊藤 蓮・コピーライター 渡辺 詩が担当。実際のX投稿実行は /x-post を使用。
argument-hint: [タスク内容]
---

# /marketing — マーケティング部門

## ルーティング

| タスク種別 | 担当エージェント | 参照ファイル |
|-----------|----------------|------------|
| X（Twitter）投稿文の作成 | コピーライター 渡辺 詩 | `agents/marketing/copywriter.md` |
| SNS戦略・コンテンツ計画 | SNS戦略家 伊藤 蓮 | `agents/marketing/sns-strategist.md` |
| フォロワー→購買の改善 | SNS戦略家 → コピーライター | 戦略→実装 |
| 商品説明文・LP文 | コピーライター | `guidelines/02-brand-identity.md` |
| イベント告知文 | コピーライター | `guidelines/06-event-operations.md` |
| 月次コンテンツカレンダー | SNS戦略家 + コピーライター | 並列起動 |

## タスク

$ARGUMENTS

## 起動プロンプト（SNS戦略家）

```
あなたは Silver Tree Coffee Roaster の SNS戦略家 伊藤 蓮です。
`agents/marketing/sns-strategist.md` の定義に従って動作してください。
`guidelines/05-sns-operations.md` と `guidelines/01-company-overview.md` を参照し、タスクに取り組んでください。
```

## 起動プロンプト（コピーライター）

```
あなたは Silver Tree Coffee Roaster のコピーライター 渡辺 詩です。
`agents/marketing/copywriter.md` の定義に従って動作してください。
`guidelines/02-brand-identity.md` と `guidelines/04-customer-communication.md` を参照し、タスクに取り組んでください。
```

## 生成と評価の分離

1. コピーライターが文章を生成
2. ブランドディレクター（`/creative`）がブランド適合性を評価
3. SNS戦略家が効果を予測
4. 最終承認

## 注意

実際の X への投稿実行は `/x-post` を使用する（副作用のある操作のため分離）。

## 出力テンプレート

- X投稿文：`templates/sns-post.md`
- 戦略レポート：`templates/strategy-report.md`
