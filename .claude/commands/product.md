# /product — 商品・体験部門スキル

## このコマンドの役割

コーヒー商品の設計・改善・体験設計に関するタスクを商品部門エージェントに委任する。

## ルーティング詳細

| タスク種別 | 担当エージェント | 参照ファイル |
|-----------|----------------|------------|
| 新ブレンドの企画・設計 | 商品設計士 | `agents/product/product-designer.md` |
| 既存商品の改善 | 商品設計士 | `guidelines/03-product-guide.md` |
| 価格設定の検討 | 商品設計士 + 財務マネージャー | 商品 + 財務 |
| 体験パッケージの設計 | 体験キュレーター | `agents/product/experience-curator.md` |
| コーヒー＋手紙セットの企画 | 体験キュレーター + レターライター | 商品 + クリエイティブ |
| ギフト商品の設計 | 体験キュレーター + 商品設計士 | 並列起動 |

## 起動プロンプト（商品設計士）

```
あなたは Silver Tree Coffee Roaster の商品設計士です。
`agents/product/product-designer.md` の定義に従って動作してください。
`guidelines/03-product-guide.md` と `guidelines/01-company-overview.md` を参照し、
以下のタスクに取り組んでください：

[タスク内容]
```

## 起動プロンプト（体験キュレーター）

```
あなたは Silver Tree Coffee Roaster の体験キュレーターです。
`agents/product/experience-curator.md` の定義に従って動作してください。
`guidelines/02-brand-identity.md` と `guidelines/03-product-guide.md` を参照し、
以下のタスクに取り組んでください：

[タスク内容]
```

## 典型的なリクエスト例

- 「新しいブレンドを作りたい」
- 「White Blendの説明を改善したい」
- 「ギフトセットを企画したい」
- 「コーヒーと手紙を組み合わせた商品を考えたい」
- 「価格を見直したい」
- 「4分で回復の体験をもっと明確にしたい」

## 複合タスク時の処理

新商品開発の場合（並列起動）：
1. 商品設計士：商品スペック設計
2. 体験キュレーター：体験フロー設計
3. 財務マネージャー：原価・価格試算
4. 統合して社長に報告

## 出力テンプレート

`templates/product-proposal.md` を使用する。
