---
name: instagram-infographic
description: Silver Tree Coffee Roaster のSNS投稿用インフォグラフィック画像を生成する。Instagram（1080×1350）・X/Twitter（1200×675）両対応。「インフォグラフィックを作りたい」「コーヒー知識を画像にして」「比較画像を作って」「ドリップ手順を図解して」「商品の特徴を画像で見せたい」「SNS用のビジュアル投稿」「X投稿に画像をつけたい」「投稿テキストからインフォグラフィックを生成」「知識系の画像投稿を作る」「画像とテキストをセットで投稿」などのときに必ず使用する。X投稿テキストを渡すだけで自動的に内容を解析してインフォグラフィックを生成し、x-post-log.mdの画像フィールドも更新できる。
---

# SNS インフォグラフィック生成スキル（Instagram / X 両対応）

## ブランドカラー

| 用途 | HEX |
|------|-----|
| 背景（ベージュ） | `#F5F0E8` |
| ダークブラウン（タイトル・強調） | `#3D2B1F` |
| コーヒーブラウン（アクセント） | `#6B4226` |
| ライトブラウン（サブ） | `#A0714F` |
| ダークグリーン（差し色） | `#2D4A3E` |
| 本文テキスト | `#2C2C2C` |
| サブテキスト | `#888880` |
| 薄ベージュ（カード背景） | `#EDE7D9` |

## フォント（Macシステムフォント）

```
タイトル：/System/Library/Fonts/ヒラギノ明朝 ProN.ttc  (index=0)
本文・見出し：/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc
強調・太字：/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc
```

## インフォグラフィックのタイプ

### タイプA：知識型（knowledge）
コーヒーの豆知識・抽出理論・産地情報・選び方など

**構成：**
- ヘッダー帯（ダークブラウン背景 + 白テキスト）：キャッチタイトル
- サブタイトル
- 3〜5点の知識ポイント（番号付き、各点に簡潔な説明）
- フッター：Silver Tree Coffee Roaster

### タイプB：比較型（comparison）
White Blend vs Dark Blend、産地A vs 産地Bなど2項目の対比

**構成：**
- ヘッダー：比較タイトル
- 2カラムレイアウト（左右に各アイテム）
- 各カラム：名称 + 属性リスト（焙煎度・香り・おすすめシーン等）
- 中央縦区切り線（ブラウン）
- フッター

### タイプC：手順型（howto）
ドリップ手順、焙煎の流れ、仕込み作業など

**構成：**
- ヘッダー：「○○の手順」タイトル
- STEP 1〜N（縦フロー）：番号（大・円形背景）+ タイトル + 説明文
- ステップ間の縦矢印or線
- フッター

### タイプD：商品型（product）
特定商品（White Blend / Dark Blend / ドリップバッグ）の紹介

**構成：**
- 商品名（大）
- キャッチコピー（明朝体・斜体風）
- 特徴・テイストノート3点
- 「BASEで取り扱っています」などのソフトCTA
- フッター

## 生成手順

### Step 1：ユーザーから情報を収集

次の情報を確認する（既に指定されていれば省略）：

1. **タイプ**：knowledge / comparison / howto / product
2. **タイトル**：メイン見出し（20字以内推奨）
3. **コンテンツ**：
   - knowledge: ポイント3〜5点（各点にタイトル+説明）
   - comparison: 比較する2項目の名前と各属性
   - howto: ステップ3〜6個（各ステップのタイトル+説明）
   - product: 商品名、キャッチコピー、特徴3点
4. **サイズ**：縦長 1080×1350（デフォルト）/ 正方形 1080×1080

### Step 2：Pythonスクリプトを生成・実行

以下のテンプレートを元に、ユーザーのコンテンツを反映した完全なPythonスクリプトを生成し、`/tmp/gen_infographic_[タイプ].py` に書き込んで実行する。

#### 共通ユーティリティ

```python
from PIL import Image, ImageDraw, ImageFont
from datetime import date
import os

W, H = 1080, 1350  # サイズ（正方形なら 1080, 1080）

# カラー定義
BG       = "#F5F0E8"
DARK_BR  = "#3D2B1F"
COFFEE   = "#6B4226"
LIGHT_BR = "#A0714F"
DARK_GR  = "#2D4A3E"
TEXT     = "#2C2C2C"
SUBTEXT  = "#888880"
CARD_BG  = "#EDE7D9"

# フォント（サイズは用途に応じて調整）
def load_font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except:
        return ImageFont.load_default()

MINCHO   = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
GOTHIC_W3 = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
GOTHIC_W6 = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

img  = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

def text_center(draw, y, text, font, color):
    """テキストを水平中央揃えで描画"""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=font, fill=color)

def draw_footer(draw):
    """Silver Tree フッターを下部に描画"""
    f = load_font(GOTHIC_W3, 24)
    text_center(draw, H - 80, "Silver Tree Coffee Roaster", f, SUBTEXT)
    # フッター上の細線
    draw.line([(80, H - 100), (W - 80, H - 100)], fill=LIGHT_BR, width=1)
```

#### タイプA：知識型テンプレート

```python
# ヘッダー帯
draw.rectangle([(0, 0), (W, 200)], fill=DARK_BR)
title_f = load_font(MINCHO, 58, index=0)
text_center(draw, 65, "タイトルテキスト", title_f, "#FFFFFF")

sub_f = load_font(GOTHIC_W3, 30)
text_center(draw, 150, "サブタイトル", sub_f, "#D4C4B0")

# アクセントライン
draw.line([(80, 220), (W - 80, 220)], fill=COFFEE, width=3)

# ポイントリスト
items = [
    ("01", "ポイントタイトル", "説明文テキスト説明文テキスト"),
    ("02", "ポイントタイトル", "説明文テキスト説明文テキスト"),
    ("03", "ポイントタイトル", "説明文テキスト説明文テキスト"),
]

y = 270
num_f   = load_font(GOTHIC_W6, 44)
pt_f    = load_font(GOTHIC_W6, 34)
desc_f  = load_font(GOTHIC_W3, 26)

for num, pt_title, desc in items:
    # カード背景
    draw.rectangle([(60, y), (W - 60, y + 150)], fill=CARD_BG, outline=None)
    # 番号（左端アクセント）
    draw.rectangle([(60, y), (110, y + 150)], fill=COFFEE)
    num_bbox = draw.textbbox((0,0), num, font=num_f)
    nx = 60 + (50 - (num_bbox[2]-num_bbox[0])) // 2
    ny = y + (150 - (num_bbox[3]-num_bbox[1])) // 2
    draw.text((nx, ny), num, font=num_f, fill="#FFFFFF")
    # テキスト
    draw.text((130, y + 25), pt_title, font=pt_f, fill=DARK_BR)
    draw.text((130, y + 75), desc, font=desc_f, fill=TEXT)
    y += 165

draw_footer(draw)
```

#### タイプB：比較型テンプレート

```python
# ヘッダー
draw.rectangle([(0, 0), (W, 180)], fill=DARK_BR)
title_f = load_font(MINCHO, 52, index=0)
text_center(draw, 60, "比較タイトル", title_f, "#FFFFFF")
text_center(draw, 130, "vs", load_font(GOTHIC_W6, 36), LIGHT_BR)

# 中央縦区切り
draw.line([(W//2, 200), (W//2, H - 110)], fill=COFFEE, width=2)

# 左カラム
left_x = 60
item_a = {"name": "White Blend", "attrs": ["焙煎度: 浅め", "香り: 柑橘・花", "おすすめ: 朝"]}
item_b = {"name": "Dark Blend",  "attrs": ["焙煎度: 深め", "香り: チョコ・木", "おすすめ: 夜"]}

name_f = load_font(GOTHIC_W6, 38)
attr_f = load_font(GOTHIC_W3, 28)

for i, (item, x) in enumerate([(item_a, 60), (item_b, W//2 + 30)]):
    draw.text((x, 220), item["name"], font=name_f, fill=DARK_BR)
    draw.line([(x, 270), (x + 460, 270)], fill=LIGHT_BR, width=1)
    ay = 290
    for attr in item["attrs"]:
        draw.text((x, ay), attr, font=attr_f, fill=TEXT)
        ay += 50

draw_footer(draw)
```

#### タイプC：手順型テンプレート

```python
# ヘッダー
draw.rectangle([(0, 0), (W, 180)], fill=DARK_GR)
title_f = load_font(MINCHO, 52, index=0)
text_center(draw, 65, "手順タイトル", title_f, "#FFFFFF")

steps = [
    ("湯温を調整する", "92〜95℃が理想。沸騰後30秒待つ。"),
    ("ペーパーをリンスする", "雑味を取るため、先にお湯を通す。"),
    ("豆を計量・挽く", "10gを中細挽きに。"),
    ("蒸らし30秒", "中心から外へ、ゆっくり注ぐ。"),
    ("3回に分けて注ぐ", "合計150mlをゆっくりと。"),
]

y = 210
num_f  = load_font(GOTHIC_W6, 40)
st_f   = load_font(GOTHIC_W6, 32)
desc_f = load_font(GOTHIC_W3, 24)

for i, (step_title, desc) in enumerate(steps, 1):
    # 丸番号
    r = 32
    cx, cy = 100, y + r
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=DARK_GR)
    n_text = str(i)
    nb = draw.textbbox((0,0), n_text, font=num_f)
    draw.text((cx - (nb[2]-nb[0])//2, cy - (nb[3]-nb[1])//2), n_text, font=num_f, fill="#FFFFFF")
    # テキスト
    draw.text((150, y + 5), step_title, font=st_f, fill=DARK_BR)
    draw.text((150, y + 45), desc, font=desc_f, fill=TEXT)
    # 次ステップへの縦線
    if i < len(steps):
        draw.line([(100, y + r*2 + 5), (100, y + 120)], fill=LIGHT_BR, width=2)
    y += 125

draw_footer(draw)
```

#### タイプD：商品型テンプレート

```python
# ヘッダー帯
draw.rectangle([(0, 0), (W, 200)], fill=DARK_BR)
name_f = load_font(MINCHO, 64, index=0)
text_center(draw, 60, "商品名", name_f, "#FFFFFF")
sub_f = load_font(GOTHIC_W3, 30)
text_center(draw, 145, "White Blend / Dark Blend", sub_f, "#D4C4B0")

draw.line([(80, 230), (W - 80, 230)], fill=COFFEE, width=3)

# キャッチコピー
catch_f = load_font(MINCHO, 42, index=0)
text_center(draw, 260, "キャッチコピーテキスト", catch_f, DARK_BR)
text_center(draw, 315, "サブキャッチテキスト", load_font(GOTHIC_W3, 30), TEXT)

# 特徴3点
features = [
    ("香り", "○○の香りが特徴的"),
    ("焙煎", "○○焙煎、○○豆を使用"),
    ("おすすめ", "○○のシーンに最適"),
]
y = 400
icon_f  = load_font(GOTHIC_W6, 32)
feat_f  = load_font(GOTHIC_W3, 28)

for label, desc in features:
    draw.rectangle([(80, y), (W-80, y+90)], fill=CARD_BG)
    draw.rectangle([(80, y), (190, y+90)], fill=COFFEE)
    lb = draw.textbbox((0,0), label, font=icon_f)
    draw.text((80 + (110-(lb[2]-lb[0]))//2, y + (90-(lb[3]-lb[1]))//2), label, font=icon_f, fill="#FFFFFF")
    draw.text((210, y + 15), desc, font=feat_f, fill=TEXT)
    y += 100

# ソフトCTA
cta_f = load_font(GOTHIC_W3, 26)
text_center(draw, y + 40, "プロフィールのリンクから BASEで取り扱っています", cta_f, SUBTEXT)

draw_footer(draw)
```

### Step 3：保存と報告

```python
# 日付ベースのファイル名で保存
today = date.today().strftime("%Y-%m-%d")
topic_slug = "topic-name"  # タイトルから英数字で生成

# プラットフォームに応じたディレクトリ
# Instagram: images/instagram/
# X:         images/x/
output_path = f"images/instagram/{today}_infographic-{topic_slug}.jpg"
img.save(output_path, "JPEG", quality=95)
print(f"✅ 保存完了: {output_path}")
```

実行後、ユーザーに以下を伝える：
- 保存先パス
- x-post-log.md の `**画像：**` フィールドに追記するか確認
- Instagram投稿のキャプション文が必要かを確認

---

## X投稿テキスト → インフォグラフィック → セット投稿（自動ワークフロー）

### 概要

X投稿テキストを受け取り、インフォグラフィックを自動生成してx-post-log.mdに紐付けるワークフロー。
**柱①（コーヒー専門知識）**の投稿に特に有効。

### 実行手順

#### Step 1：X投稿テキストを解析してインフォグラフィック構造に変換

受け取ったテキストから以下を抽出・生成する（Claudeが判断）：

| 要素 | 内容 |
|------|------|
| infographic_title | 投稿の核心を15字以内で表したタイトル |
| sub_title | 補足的なサブタイトル（10〜20字） |
| items | ポイントのリスト（タイトル + 説明、3〜4個） |
| hashtags | 元投稿のハッシュタグをそのまま使用 |
| topic_slug | ファイル名用英数字スラッグ（例：paper-rinse, 4min-habit） |

**変換ルール：**
- X投稿が箇条書き・番号リストなら → 各項目をそのままitemsに
- X投稿が説明文の場合 → 主要ポイントを3〜4点に分解してitemsに
- タイトルは投稿テーマを端的に表す（投稿の書き出しと同じでなくてよい）
- 説明文は短く・インパクトある表現に凝縮する（各20〜35字目安）

#### Step 2：プラットフォームを確認

- **X投稿に画像を追加する場合** → X形式（1200×675）、保存先：`images/x/`
- **Instagramにもクロスポストする場合** → Instagram形式（1080×1350）も追加生成

#### Step 3：X形式（1200×675）Pillowスクリプトを生成・実行

```python
from PIL import Image, ImageDraw, ImageFont
from datetime import date
import os

W, H = 1200, 675

# カラー（RGBタプル）
BG       = (245, 240, 232)
DARK_BR  = (61,  43,  31)
COFFEE   = (107, 66,  38)
LIGHT_BR = (160, 113, 79)
DARK_GR  = (45,  74,  62)
TEXT_C   = (44,  44,  44)
SUBTEXT  = (136, 136, 128)
CARD_BG  = (237, 231, 217)
WHITE    = (255, 255, 255)

MINCHO    = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
GOTHIC_W3 = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
GOTHIC_W6 = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

def lf(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except:
        return ImageFont.load_default()

img  = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# --- 左カラム（ダークグリーン背景、幅420px）---
LEFT_W = 420
draw.rectangle([(0, 0), (LEFT_W, H)], fill=DARK_GR)
draw.text((40, 38), "Silver Tree Coffee Roaster", font=lf(GOTHIC_W3, 20), fill=(180, 210, 195))
draw.line([(40, 68), (LEFT_W - 40, 68)], fill=LIGHT_BR, width=1)

# タイトル（2行に分割）
t_f = lf(MINCHO, 44, index=0)
draw.text((40, 95),  "タイトル行1",  font=t_f, fill=WHITE)
draw.text((40, 150), "タイトル行2",  font=t_f, fill=WHITE)

# サブタイトル
s_f = lf(GOTHIC_W3, 24)
draw.text((40, 215), "サブタイトル", font=s_f, fill=(200, 220, 210))

# 左下キャッチフレーズ
c_f = lf(MINCHO, 22, index=0)
draw.text((40, H - 80), "キャッチフレーズ1行目、", font=c_f, fill=(180, 210, 195))
draw.text((40, H - 50), "2行目テキスト。", font=c_f, fill=(180, 210, 195))

# --- 右カラム：ポイントカード ---
RX = LEFT_W + 35
items = [
    ("①", "ポイント1タイトル", "説明文1"),
    ("②", "ポイント2タイトル", "説明文2"),
    ("③", "ポイント3タイトル", "説明文3"),
    ("④", "ポイント4タイトル", "説明文4"),
]

num_f  = lf(GOTHIC_W6, 30)
pt_f   = lf(GOTHIC_W6, 28)
desc_f = lf(GOTHIC_W3, 21)

ITEM_H = int((H - 60) / len(items))
y = 28
for num, pt_title, desc in items:
    x2 = W - 25
    draw.rectangle([(RX, y), (x2, y + ITEM_H - 10)], fill=CARD_BG)
    draw.rectangle([(RX, y), (RX + 52, y + ITEM_H - 10)], fill=COFFEE)
    nb = draw.textbbox((0,0), num, font=num_f)
    draw.text((RX + (52-(nb[2]-nb[0]))//2, y + (ITEM_H-10-(nb[3]-nb[1]))//2), num, font=num_f, fill=WHITE)
    draw.text((RX + 65, y + 12), pt_title, font=pt_f, fill=DARK_BR)
    draw.text((RX + 65, y + 50), desc,     font=desc_f, fill=TEXT_C)
    y += ITEM_H

# フッター
draw.line([(RX, H - 38), (W - 25, H - 38)], fill=LIGHT_BR, width=1)
draw.text((RX, H - 30), "#ハッシュタグ1  #ハッシュタグ2", font=lf(GOTHIC_W3, 18), fill=SUBTEXT)

# 保存
os.makedirs("images/x", exist_ok=True)
today = date.today().strftime("%Y-%m-%d")
output = f"images/x/{today}_infographic-topic-slug.jpg"
img.save(output, "JPEG", quality=95)
print(f"✅ 保存完了: {output}")
```

#### Step 4：x-post-log.mdを自動更新

対象の投稿エントリに `**画像：**` フィールドを追加（または更新）する。

```markdown
## 2026年4月9日 12:00
**テーマ：** ブランドストーリー・想い（4分間の聖域）
**画像：** images/x/2026-04-09_infographic-4min-habit.jpg   ← 追加
**投稿文：**
（投稿テキスト...）
```

x-post-log.mdの該当エントリに `**画像：**` 行が**ない**場合は `**テーマ：**` の次の行に追加する。
すでにある場合はパスを上書きする。

#### Step 5：報告

ユーザーに以下を報告する：
- 生成した画像のプレビュー（Readツールで表示）
- 保存パス
- x-post-log.mdの更新内容
- 「次回の自動投稿（x_poster.py）でこの画像付きで投稿されます」と説明

## デザインルール

1. **余白を守る**：左右のマージンは最低60px。コンテンツを詰め込まない
2. **フォントサイズの階層**：タイトル52〜68px → サブ30〜38px → 本文24〜30px → 注釈20〜24px
3. **行間を取る**：日本語テキストは行間を文字サイズの0.5倍以上確保
4. **長いテキストは折り返し処理**：30字を超えるテキストは手動または自動で折り返す
5. **フッターを忘れない**：全タイプ共通でフッターを描画する
6. **ファイル名は日付+トピック**：`YYYY-MM-DD_infographic-[topic].jpg`

## テキスト折り返し処理（再利用コード）

```python
import textwrap

def draw_wrapped_text(draw, x, y, text, font, color, max_width, line_height):
    """長いテキストを指定幅で折り返して描画する"""
    words = list(text)  # 日本語は1字ずつ
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width:
            lines.append(current)
            current = ch
        else:
            current = test
    if current:
        lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=font, fill=color)
        y += line_height
    return y  # 次の描画開始Y座標を返す
```
