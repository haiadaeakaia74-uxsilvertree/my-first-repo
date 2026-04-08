# Silver Tree Coffee Roaster — 組織図

## 指揮系統

```
社長（オーナーロースター）
│
└── 司令塔 CLAUDE.md
    プランニング・ルーティング・統合のみ
    自分では作業しない
    │
    ├── /strategy      戦略部門
    ├── /product       商品・体験部門
    ├── /marketing     マーケティング部門
    ├── /sales         営業・顧客部門
    ├── /operations    オペレーション部門
    ├── /finance       財務部門
    └── /creative      クリエイティブ部門
```

---

## 部門別エージェント一覧

```
┌─────────────────────────────────────────────────────────────┐
│                        社長                                  │
└─────────────────────────┬───────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │  司令塔      │  CLAUDE.md
                    └──────┬──────┘
                           │
     ┌──────┬──────┬───────┼───────┬──────┬──────┐
     │      │      │       │       │      │      │
   戦略   商品   マーケ  営業・顧客  運用  財務  クリエ
```

---

## 部門詳細

### 戦略部門
```
agents/strategy/
└── chief-strategy-officer.md   高橋 誠（CSO・戦略参謀）
    ビジョン・意思決定・優先順位
```

### 商品・体験部門
```
agents/product/
├── product-designer.md         松本 匠（商品設計士）
│   ブレンド設計・価格設定
└── experience-curator.md       木村 凛（体験キュレーター）
    4分回復体験・体験パッケージ設計
```

### マーケティング部門
```
agents/marketing/
├── sns-strategist.md           伊藤 蓮（SNS戦略家）
│   SNS戦略・購買導線・数字管理
└── copywriter.md               渡辺 詩（コピーライター）
    投稿文・商品説明・全コピー
```

### 営業・顧客部門
```
agents/sales/
├── sales-strategist.md         山田 拓（営業戦略家）
│   新規獲得・マルシェ・チャネル拡大
└── customer-success.md         井上 結（顧客サクセスマネージャー）
    既存顧客維持・フォローアップ
```

### オペレーション部門
```
agents/operations/
└── operations-manager.md       橋本 律（オペレーションマネージャー）
    発送・在庫・EC・業務フロー
```

### 財務部門
```
agents/finance/
└── finance-manager.md          森 明（財務マネージャー）
    売上管理・採算計算・価格設計
```

### クリエイティブ部門
```
agents/creative/
├── letter-writer.md            岡田 栞（レターライター）
│   手紙・言葉の創作
└── brand-director.md           竹内 藍（ブランドディレクター）
    ブランド管理・世界観の番人
```

---

## ファイル構成

```
my-first-repo/
│
├── CLAUDE.md                   司令塔（エントリーポイント）
│
├── agents/                     エージェント定義
│   ├── strategy/
│   ├── product/
│   ├── marketing/
│   ├── sales/
│   ├── operations/
│   ├── finance/
│   └── creative/
│
├── .claude/commands/           スラッシュコマンド（部門別スキル）
│   ├── strategy.md             /strategy
│   ├── product.md              /product
│   ├── marketing.md            /marketing
│   ├── sales.md                /sales
│   ├── operations.md           /operations
│   ├── finance.md              /finance
│   └── creative.md             /creative
│
├── guidelines/                 社内マニュアル（全エージェント共通）
│   ├── 01-company-overview.md
│   ├── 02-brand-identity.md
│   ├── 03-product-guide.md
│   ├── 04-customer-communication.md
│   ├── 05-sns-operations.md
│   ├── 06-event-operations.md
│   ├── 07-financial-management.md
│   └── 08-agent-collaboration.md
│
├── templates/                  出力テンプレート
│   ├── strategy-report.md
│   ├── product-proposal.md
│   ├── sns-post.md
│   ├── customer-letter.md
│   ├── event-plan.md
│   └── weekly-report.md
│
└── x-post-log.md               投稿スケジュール（21投稿）
```

---

## エージェント間の連携フロー

```
【単一タスク例：投稿文を作りたい】

社長「今日の投稿作って」
  → 司令塔：/marketing を起動
    → SNS戦略家：方針・CTA設計
      → コピーライター：文章生成
        → ブランドディレクター：評価
          → 社長：最終確認


【複合タスク例：新商品をリリースしたい】

社長「新しいブレンドを出したい」
  → 司令塔：フェーズ分割して並列起動
    ├── 商品設計士：スペック設計
    ├── 体験キュレーター：体験フロー設計
    ├── 財務マネージャー：価格・採算計算
    └── ブランドディレクター：世界観評価
  → 司令塔：4つの成果物を統合
    → 社長：最終判断


【生成と評価の分離例：手紙を作りたい】

社長「商品に同梱する手紙を作って」
  → レターライター：手紙を生成（フェーズ1）
  → ブランドディレクター：評価（フェーズ2・別起動）
  → 司令塔：評価結果を統合して社長に提示
    → 社長：最終承認
```
