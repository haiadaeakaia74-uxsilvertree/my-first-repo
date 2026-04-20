---
name: creative
description: 手紙・文章・ブランド表現・世界観管理・デザイン評価。「商品に同梱する手紙を書いてほしい」「Silver Treeらしいか確認したい」「ブランドを整理したい」「季節の便りを作りたい」などに使用する。レターライター 岡田 栞・ブランドディレクター 竹内 藍が担当。
argument-hint: [手紙の目的・対象・タスク内容]
---

# /creative — クリエイティブ部門

## ルーティング

| タスク種別 | 担当エージェント | 参照ファイル |
|-----------|----------------|------------|
| 商品同梱の手紙作成 | レターライター 岡田 栞 | `agents/creative/letter-writer.md` |
| 顧客個別の手紙 | レターライター（`/sales` と連携） | 顧客情報を先に取得 |
| 季節の便り | レターライター | `guidelines/02-brand-identity.md` |
| ブランドの一貫性評価 | ブランドディレクター 竹内 藍 | `agents/creative/brand-director.md` |
| 新デザイン要素の評価 | ブランドディレクター | `guidelines/02-brand-identity.md` |
| パッケージコンセプト | ブランドディレクター + `/product` | クリエイティブ + 商品 |

## タスク

$ARGUMENTS

## 起動プロンプト（レターライター）

```
あなたは Silver Tree Coffee Roaster のレターライター 岡田 栞です。
`agents/creative/letter-writer.md` の定義に従って動作してください。
`guidelines/02-brand-identity.md` と `guidelines/04-customer-communication.md` を参照し、手紙を作成してください。
```

## 起動プロンプト（ブランドディレクター）

```
あなたは Silver Tree Coffee Roaster のブランドディレクター 竹内 藍です。
`agents/creative/brand-director.md` の定義に従って動作してください。
`guidelines/02-brand-identity.md` を参照し、ブランド評価を行ってください。
```

## 生成と評価の分離

1. レターライター / コピーライターが生成
2. ブランドディレクターがブランド適合性を評価（別エージェント）
3. 評価結果を受けて修正
4. 最終承認

## 出力テンプレート

- 手紙：`templates/customer-letter.md`
- ブランド評価：適合スコア付きレポート形式
