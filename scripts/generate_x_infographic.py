#!/usr/bin/env python3
"""Generate a Silver Tree X infographic from an x-post-log.md entry.

The script reads one scheduled post, creates a 1200x675 JPEG in images/x,
and optionally adds/updates the entry's **画像：** line.

Important: for knowledge-style posts, verify factual claims before running
this script. Do not turn unchecked temperatures, ratios, health/safety claims,
origin facts, or brewing science into an infographic.
"""

from __future__ import annotations

import argparse
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = ROOT / "x-post-log.md"
OUTPUT_DIR = ROOT / "images" / "x"

W, H = 1200, 675
LEFT_W = 420

BG = (245, 240, 232)
DARK_BR = (61, 43, 31)
COFFEE = (107, 66, 38)
LIGHT_BR = (160, 113, 79)
DARK_GR = (45, 74, 62)
TEXT_C = (44, 44, 44)
SUBTEXT = (136, 136, 128)
CARD_BG = (237, 231, 217)
WHITE = (255, 255, 255)

MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
GOTHIC_W3 = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
GOTHIC_W6 = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"


@dataclass
class Entry:
    date: str
    theme: str
    text: str
    image: Optional[str]
    start: int
    end: int
    raw: str


def font(path: str, size: int, index: int = 0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except OSError:
        return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def draw_fit_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    max_width: int,
    line_height: int,
    max_lines: int,
) -> None:
    lines: list[str] = []
    current = ""
    for ch in text:
        trial = current + ch
        width, _ = text_size(draw, trial, fnt)
        if width > max_width and current:
            lines.append(current)
            current = ch
        else:
            current = trial
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len("".join(lines)) < len(text):
        lines[-1] = lines[-1].rstrip("、。,. ") + "..."

    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height


def slugify(value: str) -> str:
    table = {
        "焙煎": "roast",
        "蒸らし": "mushi",
        "ペーパー": "paper",
        "リンス": "rinse",
        "温度": "temperature",
        "水": "water",
        "抽出": "brew",
        "香り": "aroma",
        "エチオピア": "ethiopia",
        "スペシャルティ": "specialty",
        "シングルオリジン": "single-origin",
        "グラインダー": "grinder",
        "コーヒー": "coffee",
        "回復": "recovery",
    }
    for jp, en in table.items():
        if jp in value:
            return en
    ascii_slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return ascii_slug or "post"


def parse_entries(content: str) -> list[Entry]:
    pattern = re.compile(
        r"(^## (?P<date>.+?)\n(?P<body>.*?))(?=^---\s*$\n|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    entries: list[Entry] = []
    for match in pattern.finditer(content):
        body = match.group("body")
        theme_m = re.search(r"^\*\*テーマ：\*\*\s*(.+)$", body, re.MULTILINE)
        image_m = re.search(r"^\*\*画像：\*\*\s*(.+)$", body, re.MULTILINE)
        text_m = re.search(r"^\*\*投稿文：\*\*\n(?P<text>.*?)(?=\n---\s*$|\Z)", body, re.MULTILINE | re.DOTALL)
        if not text_m:
            continue
        entries.append(
            Entry(
                date=match.group("date").strip(),
                theme=theme_m.group(1).strip() if theme_m else "",
                image=image_m.group(1).strip() if image_m else None,
                text=text_m.group("text").strip(),
                start=match.start(),
                end=match.end(),
                raw=match.group(1),
            )
        )
    return entries


def pick_entry(entries: list[Entry], date: str) -> Entry:
    matches = [entry for entry in entries if entry.date == date]
    if not matches:
        options = "\n".join(f"- {entry.date}: {entry.theme}" for entry in entries[-20:])
        raise SystemExit(f"対象日時が見つかりません: {date}\n\n最近の候補:\n{options}")
    if len(matches) > 1:
        raise SystemExit(f"対象日時が複数あります: {date}")
    return matches[0]


def is_infographic_candidate(entry: Entry) -> bool:
    if entry.image:
        return False
    text = entry.theme + "\n" + entry.text
    markers = ["柱①", "知識", "抽出", "蒸らし", "焙煎度", "香り", "水", "温度", "グラインダー", "シングルオリジン"]
    return any(marker in text for marker in markers)


def clean_post_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return "。".join(lines)


def extract_hashtags(text: str) -> str:
    tags = re.findall(r"#[^\s#]+", text)
    return "  ".join(tags[:3])


def is_question_like(sentence: str) -> bool:
    question_markers = ["ありますか", "ですか", "でしょうか", "なぜ", "何", "？", "?"]
    return any(marker in sentence for marker in question_markers)


def split_point(sentence: str) -> tuple[str, str]:
    if "、" in sentence:
        head, desc = sentence.split("、", 1)
    elif "なら" in sentence:
        head, desc = sentence.split("なら", 1)
        head = head + "なら"
    elif "は" in sentence and len(sentence) > 18:
        head, desc = sentence.split("は", 1)
        head = head + "は"
    elif len(sentence) > 18:
        head, desc = sentence[:12], sentence[12:]
    else:
        head, desc = sentence, sentence
    return head[:14], desc[:34]


def build_content(entry: Entry, title_override: Optional[str], slug_override: Optional[str]) -> tuple[str, str, list[tuple[str, str]], str, str]:
    theme = re.sub(r"（.*?）", "", entry.theme).strip()
    title = title_override or theme or clean_post_text(entry.text)[:15]
    title = title[:16]

    body = clean_post_text(entry.text)
    sentences = [s.strip(" 。") for s in re.split(r"[。！？\n]", body) if s.strip(" 。")]
    if len(sentences) < 3:
        sentences = [s.strip() for s in textwrap.wrap(body, 26) if s.strip()]

    points: list[tuple[str, str]] = []
    for sentence in sentences:
        if is_question_like(sentence):
            continue
        points.append(split_point(sentence))
        if len(points) == 4:
            break

    while len(points) < 3:
        points.append(("香りで整える", "4分の一杯で、少しだけ自分に戻る。"))

    subtitle = "知ると一杯が変わる"
    if "CAMPFIRE" in entry.text or "クラウドファンディング" in entry.text:
        subtitle = "旅するコーヒー屋の記録"
    elif "焙煎" in entry.text or "焙煎" in entry.theme:
        subtitle = "焙煎の見方"
    elif "抽出" in entry.text or "蒸らし" in entry.text or "温度" in entry.theme:
        subtitle = "抽出の小さなコツ"

    hashtags = extract_hashtags(entry.text) or "#SilverTreeCoffee"
    slug = slug_override or slugify(theme + " " + entry.text)
    return title, subtitle, points[:4], hashtags, slug


def date_prefix(date_text: str) -> str:
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_text)
    if not m:
        return "unknown-date"
    return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"


def draw_infographic(title: str, subtitle: str, points: list[tuple[str, str]], hashtags: str, output_path: Path) -> None:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (LEFT_W, H)], fill=DARK_GR)
    draw.text((40, 38), "Silver Tree Coffee Roaster", font=font(GOTHIC_W3, 20), fill=(180, 210, 195))
    draw.line([(40, 68), (LEFT_W - 40, 68)], fill=LIGHT_BR, width=1)

    title_font = font(MINCHO, 44, index=0)
    draw_fit_text(draw, (40, 96), title, title_font, WHITE, LEFT_W - 80, 55, 2)
    draw_fit_text(draw, (40, 222), subtitle, font(GOTHIC_W3, 24), (200, 220, 210), LEFT_W - 80, 34, 2)
    catch_font = font(MINCHO, 22, index=0)
    draw.text((40, H - 92), "一杯を知ると、", font=catch_font, fill=(180, 210, 195))
    draw.text((40, H - 62), "今日の味が変わる。", font=catch_font, fill=(180, 210, 195))

    rx = LEFT_W + 35
    card_count = len(points)
    item_h = int((H - 72) / card_count)
    y = 30
    num_font = font(GOTHIC_W6, 30)
    point_font = font(GOTHIC_W6, 28)
    desc_font = font(GOTHIC_W3, 21)

    for idx, (point_title, desc) in enumerate(points, 1):
        x2 = W - 25
        card_bottom = y + item_h - 12
        draw.rectangle([(rx, y), (x2, card_bottom)], fill=CARD_BG)
        draw.rectangle([(rx, y), (rx + 52, card_bottom)], fill=COFFEE)
        num = f"{idx:02d}"
        tw, th = text_size(draw, num, num_font)
        draw.text((rx + (52 - tw) // 2, y + (card_bottom - y - th) // 2), num, font=num_font, fill=WHITE)
        draw_fit_text(draw, (rx + 68, y + 14), point_title, point_font, DARK_BR, x2 - rx - 92, 34, 1)
        draw_fit_text(draw, (rx + 68, y + 56), desc, desc_font, TEXT_C, x2 - rx - 92, 28, 2)
        y += item_h

    draw.line([(rx, H - 38), (W - 25, H - 38)], fill=LIGHT_BR, width=1)
    draw_fit_text(draw, (rx, H - 30), hashtags, font(GOTHIC_W3, 18), SUBTEXT, W - rx - 25, 24, 1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "JPEG", quality=95)


def update_log(content: str, entry: Entry, image_path: str) -> str:
    updated_raw = entry.raw
    if re.search(r"^\*\*画像：\*\*.*$", updated_raw, re.MULTILINE):
        updated_raw = re.sub(r"^\*\*画像：\*\*.*$", f"**画像：** {image_path}", updated_raw, count=1, flags=re.MULTILINE)
    else:
        updated_raw = re.sub(r"(^\*\*テーマ：\*\*.*$)", rf"\1\n**画像：** {image_path}", updated_raw, count=1, flags=re.MULTILINE)
    return content[: entry.start] + updated_raw + content[entry.end :]


def generate_for_entry(entry: Entry, content: str, title_override: Optional[str], slug_override: Optional[str], update: bool) -> tuple[str, str]:
    title, subtitle, points, hashtags, slug = build_content(entry, title_override, slug_override)
    rel_path = f"images/x/{date_prefix(entry.date)}_infographic-{slug}.jpg"
    output_path = ROOT / rel_path
    draw_infographic(title, subtitle, points, hashtags, output_path)
    if update:
        content = update_log(content, entry, rel_path)
    return content, rel_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an X infographic from x-post-log.md")
    parser.add_argument("--date", help='Target entry date, e.g. "2026年5月10日 07:00"')
    parser.add_argument("--all-missing", action="store_true", help="Generate images for knowledge-style entries without an image")
    parser.add_argument("--title", help="Override image title")
    parser.add_argument("--slug", help="Override output filename slug")
    parser.add_argument("--no-update", action="store_true", help="Do not update x-post-log.md")
    args = parser.parse_args()

    if not args.date and not args.all_missing:
        parser.error("--date または --all-missing を指定してください")
    if args.all_missing and (args.title or args.slug):
        parser.error("--all-missing では --title / --slug は使えません")

    content = LOG_FILE.read_text(encoding="utf-8")
    entries = parse_entries(content)
    generated: list[tuple[Entry, str]] = []

    if args.all_missing:
        targets = [entry for entry in entries if is_infographic_candidate(entry)]
        if not targets:
            print("画像未設定の知識系投稿はありません。")
            return
        for entry in targets:
            content, rel_path = generate_for_entry(entry, content, None, None, update=not args.no_update)
            generated.append((entry, rel_path))
            entries = parse_entries(content)
    else:
        entry = pick_entry(entries, args.date)
        content, rel_path = generate_for_entry(entry, content, args.title, args.slug, update=not args.no_update)
        generated.append((entry, rel_path))

    if not args.no_update:
        LOG_FILE.write_text(content, encoding="utf-8")

    for entry, rel_path in generated:
        print(f"保存完了: {rel_path}")
        print(f"対象投稿: {entry.date} / {entry.theme}")
    print(f"生成枚数: {len(generated)}")
    print(f"ログ更新: {'なし' if args.no_update else 'あり'}")


if __name__ == "__main__":
    main()
