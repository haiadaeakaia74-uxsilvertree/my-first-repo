# /marketing — マーケティング部門スキル

## このコマンドの役割

SNS運用・コンテンツ制作・コピーライティングに関するタスクをマーケティング部門に委任する。

## ルーティング詳細

| タスク種別 | 担当エージェント | 参照ファイル |
|-----------|----------------|------------|
| X（Twitter）投稿文の作成 | コピーライター | `agents/marketing/copywriter.md` |
| SNS戦略・コンテンツ計画 | SNS戦略家 | `agents/marketing/sns-strategist.md` |
| フォロワー→購買の改善 | SNS戦略家 → コピーライター | 戦略→実装 |
| 商品説明文・LP文 | コピーライター | `guidelines/02-brand-identity.md` |
| イベント告知文 | コピーライター | `guidelines/06-event-operations.md` |
| 月次コンテンツカレンダー | SNS戦略家 + コピーライター | 並列起動 |

## 起動プロンプト（SNS戦略家）

```
あなたは Silver Tree Coffee Roaster の SNS戦略家です。
`agents/marketing/sns-strategist.md` の定義に従って動作してください。
`guidelines/05-sns-operations.md` と `guidelines/01-company-overview.md` を参照し、
以下のタスクに取り組んでください：

[タスク内容]
```

## 起動プロンプト（コピーライター）

```
あなたは Silver Tree Coffee Roaster のコピーライターです。
`agents/marketing/copywriter.md` の定義に従って動作してください。
`guidelines/02-brand-identity.md` と `guidelines/04-customer-communication.md` を参照し、
以下のタスクに取り組んでください：

[タスク内容]
```

## 典型的なリクエスト例

- 「今日のX投稿を作ってほしい」
- 「SNSから購買につながる仕掛けを作りたい」
- 「来月のコンテンツ計画を立てたい」
- 「BASEの商品説明文を改善したい」
- 「マルシェの告知文を書いてほしい」
- 「フォロワーが増えない、どうすればいい？」

## 生成と評価の分離

コンテンツ生成後の品質評価：
1. コピーライターが文章を生成
2. ブランドディレクターがブランド適合性を評価
3. SNS戦略家が効果を予測
4. 社長が最終承認

## 出力テンプレート

- X投稿：`templates/sns-post.md`
- 戦略レポート：`templates/strategy-report.md`
