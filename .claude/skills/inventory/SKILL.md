---
name: inventory
description: Silver Tree Coffee Roasterの在庫を管理・可視化する。「在庫を確認したい」「在庫管理」「在庫が足りてるか確認して」「何がどれくらい残ってるか」「棒グラフで在庫を見たい」「補充が必要なものを教えて」などのときに必ず使用する。在庫数を入力するだけで、棒グラフ付きHTML可視化ファイルを生成し、不足アイテムと補充タイミングを即座に把握できる。
argument-hint: [在庫データ（任意）]
---

# /inventory — 在庫管理・可視化スキル

Silver Tree Coffee Roaster の在庫状況を棒グラフで可視化し、補充判断をサポートする。

---

## 管理対象アイテム一覧

| カテゴリ | アイテム | 最低在庫ライン | 補充単位の目安 |
|---------|---------|-------------|-------------|
| **豆** | White Blend（生豆） | 500g | 1kg〜 |
| **豆** | Dark Blend（生豆） | 500g | 1kg〜 |
| **販売用** | White Blend 袋（100g） | 5袋 | 10袋〜 |
| **販売用** | Dark Blend 袋（100g） | 5袋 | 10袋〜 |
| **販売用** | ドリップバッグ | 10個 | 20個〜 |
| **手紙関連** | おみくじ手紙 | 20枚 | 30枚〜 |
| **手紙関連** | 封筒 | 20枚 | 50枚〜 |
| **手紙関連** | シーリングワックス | 1本 | 3本〜 |
| **消耗品** | ペーパーフィルター | 50枚 | 100枚〜 |
| **消耗品** | 紙コップ | 20個 | 50個〜 |
| **消耗品** | 袋（手提げ）| 10枚 | 30枚〜 |

---

## Step 1：在庫データの入力

`$ARGUMENTS` に在庫データがあればそれを使う。なければ以下の形式で入力を求める：

```
アイテム名：現在の在庫数（単位）

例：
White Blend 袋：8袋
Dark Blend 袋：3袋
おみくじ手紙：15枚
封筒：45枚
ペーパーフィルター：30枚
```

---

## Step 2：HTMLファイルの生成

**必ず以下の標準フォーマットを使用すること。勝手に簡略化しない。**

在庫データを受け取ったら `/tmp/inventory_[YYYYMMDD].html` に保存し、`open` コマンドで自動的にブラウザで開く。

### 標準フォーマット（必須）

以下の6要素をすべて含めること：

1. **ヘッダー**：タイトル＋日付・発注ライン・総在庫をサブテキストで
2. **サマリーカード4枚**：🔴発注以下・🟠ライン接近・🟢正常・総在庫(kg)
3. **赤アラートセクション**：発注ライン以下の銘柄を列挙（border-left: 3px solid #c0392b）
4. **オレンジ通知セクション**：発注ライン接近（2kg〜2.6kg）の銘柄（border-left: 3px solid #e67e22）
5. **縦棒グラフ**：在庫量(kg)・発注ライン赤点線付き・Chart.js
6. **横棒グラフ**：残存率(%)・5kg基準・Chart.js
7. **詳細テーブル**：銘柄・現在庫・発注ライン・状態タグ・備考バッジ
8. **フッター**：Silver Tree Coffee Roaster — 香川県東かがわ市 ｜ 日付

### CSSクラス定義（必須）

```css
body { font-family: "Hiragino Mincho ProN", Georgia, serif; background: #F8F4EE; color: #1C1C1C; max-width: 960px; margin: 0 auto; padding: 40px 20px; }
h1 { font-size: 1.4rem; font-weight: normal; color: #2D4A3E; border-bottom: 1px solid #D4C5A9; padding-bottom: 12px; margin-bottom: 8px; }
.date { color: #6B4226; font-size: 0.85rem; margin-bottom: 32px; }
.summary-row { display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }
.summary-card { background: white; border-radius: 8px; padding: 16px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); flex: 1; min-width: 130px; text-align: center; }
.summary-card .label { font-size: 0.75rem; color: #6B4226; margin-bottom: 6px; }
.summary-card .value { font-size: 1.6rem; font-weight: bold; }
.summary-card.danger .value { color: #c0392b; }
.summary-card.warning .value { color: #e67e22; }
.summary-card.ok .value { color: #2D4A3E; }
.alert-section { background: #fff8f0; border-left: 3px solid #c0392b; padding: 16px 20px; border-radius: 0 8px 8px 0; margin-bottom: 28px; }
.alert-title { font-size: 0.85rem; color: #c0392b; margin-bottom: 10px; font-weight: bold; }
.alert-item { font-size: 0.9rem; padding: 5px 0; }
.notice-section { background: #fef9f0; border-left: 3px solid #e67e22; padding: 16px 20px; border-radius: 0 8px 8px 0; margin-bottom: 28px; }
.notice-title { font-size: 0.85rem; color: #e67e22; margin-bottom: 10px; font-weight: bold; }
.chart-container { background: white; border-radius: 8px; padding: 24px; margin-bottom: 28px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.chart-title { font-size: 0.9rem; color: #6B4226; margin-bottom: 16px; font-weight: normal; letter-spacing: 0.05em; }
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 28px; }
th { background: #2D4A3E; color: white; padding: 10px 16px; text-align: left; font-weight: normal; font-size: 0.8rem; letter-spacing: 0.05em; }
td { padding: 10px 16px; border-bottom: 1px solid #F8F4EE; }
tr:last-child td { border-bottom: none; }
.tag { padding: 2px 10px; border-radius: 4px; font-size: 0.75rem; display: inline-block; }
.tag-danger { background: #fde8e8; color: #c0392b; }
.tag-warning { background: #fef3e2; color: #e67e22; }
.tag-ok { background: #e8f4f0; color: #2D4A3E; }
.tag-full { background: #e8f4f0; color: #2D4A3E; font-weight: bold; }
.badge { padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; margin-left: 4px; }
.badge-base { background: #D4C5A9; color: #6B4226; }
.badge-end { background: #fde8e8; color: #c0392b; }
.badge-water { background: #e8f0f4; color: #2D4A3E; }
.badge-roast { background: #e8f4f0; color: #2D4A3E; }
footer { text-align: center; color: #D4C5A9; font-size: 0.75rem; margin-top: 48px; }
```

### カラーコード（在庫状態別）

| 状態 | 条件 | 色 |
|------|------|-----|
| 発注以下 | 現在庫 < 2kg | 赤 `rgba(192,57,43,0.75)` |
| 要注意 | 2kg ≤ 現在庫 < 2.6kg | オレンジ `rgba(230,126,34,0.75)` |
| 正常 | 2.6kg 以上 | ディープグリーン `rgba(45,74,62,0.75)` |

### 発注ライン赤点線（縦棒グラフ必須プラグイン）

```javascript
plugins: [{
  id: 'orderLine',
  afterDraw(chart) {
    const { ctx, chartArea: { left, right }, scales: { y } } = chart;
    const yPos = y.getPixelForValue(2.0);
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(left, yPos);
    ctx.lineTo(right, yPos);
    ctx.lineWidth = 2;
    ctx.strokeStyle = 'rgba(192,57,43,0.6)';
    ctx.setLineDash([6, 3]);
    ctx.stroke();
    ctx.fillStyle = 'rgba(192,57,43,0.8)';
    ctx.font = '11px sans-serif';
    ctx.fillText('発注ライン 2kg', right - 90, yPos - 6);
    ctx.restore();
  }
}]
```

### 参照ファイル（正規フォーマットの実例）

`/tmp/inventory_20260421.html` — 必ずこのファイルを参照してフォーマットを確認すること。

---

## Step 3：テキストサマリーの出力

HTMLファイル生成後、チャット上にもサマリーを出力する。

```
## 在庫サマリー [日付]

🔴 即補充が必要（最低ラインを下回っている）
  - [アイテム名]：現在 __ / 最低 __

🟠 注意（近日中に補充推奨）
  - [アイテム名]：現在 __ / 最低 __

🟢 正常
  - [アイテム名]：__ ほか __点

---
📄 詳細グラフ：/tmp/inventory_[YYYYMMDD].html
   ターミナルで open /tmp/inventory_[YYYYMMDD].html で確認できます。
```

---

## Step 4：補充メモの生成（任意）

「補充リストを出して」と言われたら、以下フォーマットで出力する：

```
## 補充リスト [日付]

□ [アイテム名] — [補充量の目安] （現在 __）
□ [アイテム名] — [補充量の目安] （現在 __）

合計予算目安：約 ____円
```
