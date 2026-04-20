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

在庫データを受け取ったら、Chart.js を使った棒グラフ付きHTMLファイルを生成して `/tmp/inventory_[YYYYMMDD].html` に保存する。

### HTMLテンプレート

以下の構造でHTMLを生成すること：

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Silver Tree — 在庫管理 [日付]</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {
      font-family: "Hiragino Mincho ProN", Georgia, serif;
      background: #F8F4EE;
      color: #1C1C1C;
      max-width: 900px;
      margin: 0 auto;
      padding: 40px 20px;
    }
    h1 {
      font-size: 1.4rem;
      font-weight: normal;
      color: #2D4A3E;
      border-bottom: 1px solid #D4C5A9;
      padding-bottom: 12px;
      margin-bottom: 8px;
    }
    .date {
      color: #6B4226;
      font-size: 0.85rem;
      margin-bottom: 40px;
    }
    .chart-container {
      background: white;
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 32px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .chart-title {
      font-size: 0.9rem;
      color: #6B4226;
      margin-bottom: 16px;
      font-weight: normal;
      letter-spacing: 0.05em;
    }
    .alert-section {
      background: #fff8f0;
      border-left: 3px solid #6B4226;
      padding: 16px 20px;
      border-radius: 0 8px 8px 0;
      margin-bottom: 24px;
    }
    .alert-title {
      font-size: 0.85rem;
      color: #6B4226;
      margin-bottom: 10px;
    }
    .alert-item {
      font-size: 0.9rem;
      padding: 4px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .status-danger { color: #c0392b; }
    .status-warning { color: #e67e22; }
    .status-ok { color: #2D4A3E; }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
      background: white;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    th {
      background: #2D4A3E;
      color: white;
      padding: 10px 16px;
      text-align: left;
      font-weight: normal;
      font-size: 0.8rem;
      letter-spacing: 0.05em;
    }
    td {
      padding: 10px 16px;
      border-bottom: 1px solid #F8F4EE;
    }
    tr:last-child td { border-bottom: none; }
    .tag-danger {
      background: #fde8e8;
      color: #c0392b;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
    }
    .tag-warning {
      background: #fef3e2;
      color: #e67e22;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
    }
    .tag-ok {
      background: #e8f4f0;
      color: #2D4A3E;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
    }
    footer {
      text-align: center;
      color: #D4C5A9;
      font-size: 0.75rem;
      margin-top: 48px;
    }
  </style>
</head>
<body>
  <h1>Silver Tree Coffee Roaster — 在庫管理</h1>
  <p class="date">[日付] 現在</p>

  <!-- アラートセクション -->
  <div class="alert-section">
    <div class="alert-title">⚠ 要確認アイテム</div>
    [要補充・注意アイテムをリスト表示]
  </div>

  <!-- 棒グラフ（全体） -->
  <div class="chart-container">
    <div class="chart-title">在庫一覧（現在数 vs 最低ライン）</div>
    <canvas id="inventoryChart" height="300"></canvas>
  </div>

  <!-- カテゴリ別グラフ -->
  <div class="chart-container">
    <div class="chart-title">カテゴリ別 在庫率（%）</div>
    <canvas id="categoryChart" height="200"></canvas>
  </div>

  <!-- 詳細テーブル -->
  <table>
    <thead>
      <tr>
        <th>アイテム</th>
        <th>現在庫</th>
        <th>最低ライン</th>
        <th>状態</th>
      </tr>
    </thead>
    <tbody>
      [各アイテムの行を動的に生成]
    </tbody>
  </table>

  <footer>Silver Tree Coffee Roaster — 香川県東かがわ市</footer>

  <script>
    // データ
    const items = [データを配列で];

    // 棒グラフ：現在庫 vs 最低ライン
    const ctx1 = document.getElementById('inventoryChart').getContext('2d');
    new Chart(ctx1, {
      type: 'bar',
      data: {
        labels: items.map(i => i.name),
        datasets: [
          {
            label: '現在庫',
            data: items.map(i => i.current),
            backgroundColor: items.map(i =>
              i.current < i.min ? 'rgba(192,57,43,0.7)' :
              i.current < i.min * 1.5 ? 'rgba(230,126,34,0.7)' :
              'rgba(45,74,62,0.7)'
            ),
            borderRadius: 4,
          },
          {
            label: '最低ライン',
            data: items.map(i => i.min),
            backgroundColor: 'rgba(212,197,169,0.4)',
            borderRadius: 4,
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
  </script>
</body>
</html>
```

### カラーコード（在庫状態別）

| 状態 | 条件 | 色 |
|------|------|-----|
| 危険（要即補充） | 現在庫 < 最低ライン | 赤 `#c0392b` |
| 注意（近日補充） | 最低ライン ≤ 現在庫 < 最低ライン×1.5 | オレンジ `#e67e22` |
| 正常 | 最低ライン×1.5 以上 | ディープグリーン `#2D4A3E` |

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
