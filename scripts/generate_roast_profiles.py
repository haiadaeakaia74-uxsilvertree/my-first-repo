#!/usr/bin/env python3
"""
Generate roast profile HTML from roast-logs/*.md.

The source of truth stays in Markdown. This script turns one or more roast logs
into browser-friendly profile pages and can rebuild roast-profiles/index.html.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROAST_LOG_DIR = ROOT / "roast-logs"
PROFILE_DIR = ROOT / "roast-profiles"


@dataclass
class TempPoint:
    minute: float
    label: str
    drum: float | None
    bean: float | None
    power: str = ""
    note: str = ""


@dataclass
class Batch:
    name: str
    start: str = ""
    green_weight: float | None = None
    roasted_weight: float | None = None
    yield_pct: float | None = None
    loss_pct: float | None = None
    roast_ratio: float | None = None
    drop_time: str = ""
    rows: list[TempPoint] = field(default_factory=list)
    summary: dict[str, str] = field(default_factory=dict)


@dataclass
class RoastLog:
    path: Path
    date: str = ""
    bean: str = ""
    purpose: str = ""
    drum: str = ""
    target: str = ""
    weather: str = ""
    source: str = ""
    notes: list[str] = field(default_factory=list)
    batches: list[Batch] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return self.path.stem.replace("_", "-")


def clean_cell(value: str) -> str:
    value = re.sub(r"<br\s*/?>", " / ", value)
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"`(.*?)`", r"\1", value)
    return value.replace("&nbsp;", " ").strip()


def strip_unit_number(value: str) -> float | None:
    m = re.search(r"[-+]?\d+(?:\.\d+)?", value.replace(",", ""))
    return float(m.group(0)) if m else None


def parse_minute(value: str) -> float | None:
    value = clean_cell(value)
    if not value:
        return None
    m = re.search(r"(\d{1,2}):(\d{2})", value)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60
    m = re.search(r"(\d+(?:\.\d+)?)\s*分", value)
    if m:
        return float(m.group(1))
    return strip_unit_number(value)


def minute_label(minute: float) -> str:
    whole = int(minute)
    sec = round((minute - whole) * 60)
    return f"{whole}:{sec:02d}"


def parse_temp(value: str) -> float | None:
    if "不明" in value or "—" in value:
        return None
    return strip_unit_number(value)


def parse_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        parts = [clean_cell(p) for p in lines[i].strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-{2,}:?", p.replace(" ", "")) for p in parts):
            rows.append(parts)
        i += 1
    return rows, i


def meta_from_line(line: str) -> tuple[str, str] | None:
    m = re.match(r"\*\*(.+?)：\*\*\s*(.+?)\s*$", line.strip())
    if not m:
        return None
    return clean_cell(m.group(1)), clean_cell(m.group(2))


def is_temp_table(header: list[str]) -> bool:
    joined = " ".join(header)
    return ("時間" in joined or "経過時間" in joined) and "豆温" in joined


def row_to_temp(row: list[str]) -> TempPoint | None:
    if len(row) < 3:
        return None
    minute = parse_minute(row[0])
    if minute is None:
        return None
    drum = parse_temp(row[1])
    bean = parse_temp(row[2])
    power = row[3] if len(row) > 3 else ""
    note = row[4] if len(row) > 4 else ""
    return TempPoint(minute=minute, label=minute_label(minute), drum=drum, bean=bean, power=power, note=note)


def update_batch_numbers(batch: Batch) -> None:
    if batch.green_weight and batch.roasted_weight:
        batch.yield_pct = round(batch.roasted_weight / batch.green_weight * 100, 1)
        batch.loss_pct = round(100 - batch.yield_pct, 1)
        batch.roast_ratio = round(batch.green_weight / batch.roasted_weight, 3)


def apply_summary(batch: Batch) -> None:
    for key, value in batch.summary.items():
        if key in ("生豆重量", "生豆投入量"):
            batch.green_weight = strip_unit_number(value)
        elif key == "焙煎後重量":
            batch.roasted_weight = strip_unit_number(value)
        elif key == "歩留まり":
            batch.yield_pct = strip_unit_number(value)
        elif key == "重量減少率":
            batch.loss_pct = strip_unit_number(value)
        elif "焙煎率" in key:
            batch.roast_ratio = strip_unit_number(value)
        elif key in ("排出", "排出時間"):
            batch.drop_time = value
        elif key == "開始":
            batch.start = value
    update_batch_numbers(batch)


def parse_log(path: Path) -> RoastLog:
    lines = path.read_text(encoding="utf-8").splitlines()
    roast = RoastLog(path=path)
    current: Batch | None = None
    has_detailed_batches = any(re.match(r"^##+\s+バッチ", line) for line in lines)
    i = 0
    while i < len(lines):
        line = lines[i]
        meta = meta_from_line(line)
        if meta:
            key, value = meta
            if key == "日付":
                roast.date = value
            elif key == "豆":
                roast.bean = value
            elif key in ("用途", "目的"):
                roast.purpose = value
            elif key == "ドラム":
                roast.drum = value
            elif key == "狙い":
                roast.target = value
            elif key in ("天候 / 気温", "天候・気温・湿度"):
                roast.weather = value
            elif key == "記録元":
                roast.source = value
            i += 1
            continue

        heading = re.match(r"^##+\s+(.+?)\s*$", line)
        if heading:
            title = clean_cell(heading.group(1))
            if title.startswith("バッチ"):
                current = Batch(name=title)
                roast.batches.append(current)
            elif title in ("数値データ", "温度ログ") and not roast.batches:
                current = Batch(name="バッチ1")
                roast.batches.append(current)
            i += 1
            continue

        if line.lstrip().startswith("|"):
            table, next_i = parse_table(lines, i)
            if table:
                header = table[0]
                body = table[1:]
                if len(header) == 2 and current:
                    for row in body:
                        if len(row) >= 2:
                            current.summary[row[0]] = row[1]
                    apply_summary(current)
                elif is_temp_table(header) and current:
                    current.rows = [p for row in body if (p := row_to_temp(row))]
                elif (
                    not has_detailed_batches
                    and header
                    and header[0] == "項目"
                    and len(header) > 2
                    and "比較サマリー" in "\n".join(lines[max(0, i - 4):i])
                ):
                    # Comparison tables without detailed temp rows: make one batch per column.
                    labels = header[1:]
                    if not roast.batches:
                        roast.batches = [Batch(name=f"バッチ{idx + 1}：{label}") for idx, label in enumerate(labels)]
                    for row in body:
                        key = row[0]
                        for idx, value in enumerate(row[1:]):
                            if idx < len(roast.batches):
                                roast.batches[idx].summary[key] = value
                    for b in roast.batches:
                        apply_summary(b)
            i = next_i
            continue

        if line.startswith("- ") and len(roast.notes) < 6:
            roast.notes.append(clean_cell(line[2:]))
        i += 1

    if not roast.date:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
        roast.date = m.group(1) if m else ""
    for batch in roast.batches:
        if not batch.green_weight and batch.summary.get("生豆投入量"):
            batch.green_weight = strip_unit_number(batch.summary["生豆投入量"])
        update_batch_numbers(batch)
    return roast


def ror_points(rows: list[TempPoint]) -> list[dict[str, float]]:
    points = [p for p in rows if p.bean is not None]
    out: list[dict[str, float]] = []
    for prev, cur in zip(points, points[1:]):
        delta_time = cur.minute - prev.minute
        if delta_time <= 0:
            continue
        out.append({"x": round((prev.minute + cur.minute) / 2, 3), "y": round((cur.bean - prev.bean) / delta_time, 2)})
    return out


def chart_points(rows: list[TempPoint], attr: str) -> list[dict[str, float]]:
    points = []
    for row in rows:
        value = getattr(row, attr)
        if value is not None:
            points.append({"x": round(row.minute, 3), "y": value})
    return points


def event_markers(rows: list[TempPoint]) -> list[dict[str, str | float]]:
    events = []
    patterns = [
        ("黄変", "#c0772a"),
        ("1ハゼ開始", "#2D4A3E"),
        ("1ハゼ終了", "#6B4226"),
        ("火止め", "#8e3b2f"),
        ("排出", "#555555"),
    ]
    for row in rows:
        for label, color in patterns:
            if label in row.note:
                events.append({"t": round(row.minute, 3), "label": label, "color": color})
                break
    return events


def e(value: object) -> str:
    return html.escape("" if value is None else str(value))


def fmt(value: float | None, suffix: str = "") -> str:
    return "—" if value is None else f"{value:.1f}{suffix}"


def render_profile(roast: RoastLog) -> str:
    batch_count = len(roast.batches)
    green_total = sum(b.green_weight or 0 for b in roast.batches)
    roasted_total = sum(b.roasted_weight or 0 for b in roast.batches)
    avg_yield = (roasted_total / green_total * 100) if green_total and roasted_total else None
    max_time = max((p.minute for b in roast.batches for p in b.rows), default=15)
    max_time = max(13, round(max_time + 1))
    batch_cards = []
    chart_scripts = []
    for idx, batch in enumerate(roast.batches, 1):
        rows_html = "\n".join(
            f"<tr><td>{e(p.label)}</td><td class=\"drum\">{e('' if p.drum is None else int(p.drum))}</td><td class=\"bean\">{e('' if p.bean is None else int(p.bean))}</td><td>{e(p.power)}</td><td>{e(p.note)}</td></tr>"
            for p in batch.rows
        ) or "<tr><td colspan=\"5\">温度ログなし</td></tr>"
        canvas = f"batch{idx}Chart"
        batch_cards.append(f"""
  <div class="section-header">{e(batch.name)}</div>
  <div class="stats-row">
    <div class="stat-card"><div class="s-label">生豆</div><div class="s-value">{fmt(batch.green_weight, 'g')}</div></div>
    <div class="stat-card"><div class="s-label">焙煎後</div><div class="s-value">{fmt(batch.roasted_weight, 'g')}</div></div>
    <div class="stat-card"><div class="s-label">歩留まり</div><div class="s-value">{fmt(batch.yield_pct, '%')}</div></div>
    <div class="stat-card"><div class="s-label">減少率</div><div class="s-value">{fmt(batch.loss_pct, '%')}</div></div>
  </div>
  <div class="chart-card">
    <div class="chart-title">{e(batch.name)} 温度プロファイル / ROR</div>
    <canvas id="{canvas}" height="320"></canvas>
  </div>
  <table>
    <thead><tr><th>時間</th><th>ドラム</th><th>豆温</th><th>火力</th><th>メモ</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
""")
        chart_scripts.append(
            f"makeChart('{canvas}', {json.dumps(chart_points(batch.rows, 'drum'), ensure_ascii=False)}, "
            f"{json.dumps(chart_points(batch.rows, 'bean'), ensure_ascii=False)}, "
            f"{json.dumps(ror_points(batch.rows), ensure_ascii=False)}, "
            f"{json.dumps(event_markers(batch.rows), ensure_ascii=False)});"
        )

    notes = "".join(f"<li>{e(n)}</li>" for n in roast.notes) or "<li>Markdownログから自動生成。</li>"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Silver Tree — {e(roast.date)} Roast Profile</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{ font-family: "Hiragino Mincho ProN", "Yu Mincho", Georgia, serif; background:#F8F4EE; color:#1C1C1C; max-width:1080px; margin:0 auto; padding:48px 20px; }}
    .nav {{ font-size:.78rem; color:#888; margin-bottom:28px; }}
    .nav a {{ color:#2D4A3E; text-decoration:none; }}
    h1 {{ font-size:1.35rem; font-weight:normal; color:#2D4A3E; border-bottom:1px solid #D4C5A9; padding-bottom:12px; margin-bottom:8px; }}
    .subtitle {{ color:#6B4226; font-size:.85rem; margin-bottom:34px; line-height:1.8; }}
    .stats-row {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-bottom:24px; }}
    .stat-card, .note, .chart-card, table {{ background:#fff; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,.07); }}
    .stat-card {{ padding:16px 18px; text-align:center; }}
    .s-label {{ font-size:.72rem; color:#6B4226; margin-bottom:5px; }}
    .s-value {{ font-size:1.35rem; font-weight:bold; color:#2D4A3E; }}
    .section-header {{ font-size:.78rem; color:#888; letter-spacing:.1em; text-transform:uppercase; margin:32px 0 14px; padding-bottom:6px; border-bottom:1px solid #E8E0D4; }}
    .note {{ border-left:3px solid #2D4A3E; border-radius:0 8px 8px 0; padding:16px 20px; line-height:1.8; font-size:.9rem; }}
    .chart-card {{ padding:24px 26px; margin-bottom:16px; }}
    .chart-title {{ color:#6B4226; font-size:.95rem; margin-bottom:14px; }}
    table {{ width:100%; border-collapse:collapse; font-size:.86rem; overflow:hidden; margin-bottom:16px; }}
    th {{ background:#2D4A3E; color:#fff; padding:10px 12px; text-align:left; font-weight:normal; font-size:.78rem; }}
    td {{ padding:9px 12px; border-bottom:1px solid #F8F4EE; vertical-align:top; }}
    tr:last-child td {{ border-bottom:none; }}
    .drum {{ color:#D35400; font-weight:bold; }}
    .bean {{ color:#1A5276; font-weight:bold; }}
    footer {{ text-align:center; color:#D4C5A9; font-size:.73rem; margin-top:48px; }}
    @media (max-width:760px) {{ .stats-row {{ grid-template-columns:1fr; }} body {{ padding:32px 14px; }} }}
  </style>
</head>
<body>
  <div class="nav"><a href="index.html">← 焙煎プロファイル一覧</a>　｜　自動生成</div>
  <h1>{e(roast.bean or roast.slug)} 焙煎プロファイル</h1>
  <p class="subtitle">{e(roast.date)}　｜　狙い：{e(roast.target or '未記録')}　｜　ドラム：{e(roast.drum or '未記録')}</p>
  <div class="stats-row">
    <div class="stat-card"><div class="s-label">バッチ数</div><div class="s-value">{batch_count}</div></div>
    <div class="stat-card"><div class="s-label">生豆合計</div><div class="s-value">{green_total:.1f}g</div></div>
    <div class="stat-card"><div class="s-label">焙煎後合計</div><div class="s-value">{roasted_total:.1f}g</div></div>
    <div class="stat-card"><div class="s-label">平均歩留まり</div><div class="s-value">{fmt(avg_yield, '%')}</div></div>
  </div>
  <div class="section-header">読み取りメモ</div>
  <div class="note"><ul>{notes}</ul></div>
{''.join(batch_cards)}
  <footer>Silver Tree Coffee Roaster — generated from {e(roast.path.name)} at {generated_at}</footer>
  <script>
    const eventMarkerPlugin = {{
      id: 'eventMarkers',
      afterDraw(chart, args, pluginOptions) {{
        const {{ ctx, chartArea: {{ top, bottom }}, scales: {{ x }} }} = chart;
        (pluginOptions.events || []).forEach(ev => {{
          const xPos = x.getPixelForValue(ev.t);
          ctx.save();
          ctx.beginPath();
          ctx.moveTo(xPos, top);
          ctx.lineTo(xPos, bottom);
          ctx.strokeStyle = ev.color;
          ctx.lineWidth = 1.2;
          ctx.setLineDash([4, 3]);
          ctx.stroke();
          ctx.fillStyle = ev.color;
          ctx.font = '11px "Hiragino Mincho ProN", serif';
          ctx.textAlign = 'center';
          ctx.fillText(ev.label, xPos, top + 14);
          ctx.restore();
        }});
      }}
    }};
    function makeChart(canvasId, drum, bean, ror, events) {{
      new Chart(document.getElementById(canvasId), {{
        type: 'scatter',
        data: {{ datasets: [
          {{ label: 'ドラム温度', data: drum, yAxisID: 'y', showLine: true, borderColor: '#D35400', backgroundColor: '#D35400', tension: .25, pointRadius: 3 }},
          {{ label: '豆温', data: bean, yAxisID: 'y', showLine: true, borderColor: '#1A5276', backgroundColor: '#1A5276', tension: .25, pointRadius: 3 }},
          {{ label: 'ROR(豆温)', data: ror, yAxisID: 'ror', showLine: true, borderColor: '#6DBAA0', backgroundColor: '#6DBAA0', borderDash: [4, 3], tension: .25, pointRadius: 2 }}
        ]}},
        options: {{
          responsive: true,
          interaction: {{ mode: 'nearest', intersect: false }},
          scales: {{
            x: {{ type: 'linear', min: 0, max: {max_time}, title: {{ display: true, text: '経過時間（分）' }}, ticks: {{ stepSize: 1 }} }},
            y: {{ min: 60, max: 240, title: {{ display: true, text: '温度（℃）' }} }},
            ror: {{ position: 'right', min: 0, max: 30, title: {{ display: true, text: 'ROR（℃/min）' }}, grid: {{ drawOnChartArea: false }} }}
          }},
          plugins: {{ legend: {{ position: 'top' }}, eventMarkers: {{ events }} }}
        }},
        plugins: [eventMarkerPlugin]
      }});
    }}
    {''.join(chart_scripts)}
  </script>
</body>
</html>
"""


def render_index(roasts: list[RoastLog]) -> str:
    cards = []
    total_batches = sum(len(r.batches) for r in roasts)
    yields = [b.yield_pct for r in roasts for b in r.batches if b.yield_pct is not None]
    avg_yield = sum(yields) / len(yields) if yields else 0
    total_green = sum(b.green_weight or 0 for r in roasts for b in r.batches)
    total_roasted = sum(b.roasted_weight or 0 for r in roasts for b in r.batches)
    latest_date = max((r.date for r in roasts if r.date), default="—")
    bean_totals: dict[str, dict[str, float | int]] = {}
    for roast in roasts:
        name = roast.bean or roast.slug
        if name not in bean_totals:
            bean_totals[name] = {"batches": 0, "green": 0.0, "roasted": 0.0}
        for batch in roast.batches:
            bean_totals[name]["batches"] = int(bean_totals[name]["batches"]) + 1
            bean_totals[name]["green"] = float(bean_totals[name]["green"]) + (batch.green_weight or 0)
            bean_totals[name]["roasted"] = float(bean_totals[name]["roasted"]) + (batch.roasted_weight or 0)

    bean_rows = []
    for bean, values in sorted(bean_totals.items(), key=lambda item: float(item[1]["green"]), reverse=True):
        green = float(values["green"])
        roasted = float(values["roasted"])
        yield_text = f"{roasted / green * 100:.1f}%" if green and roasted else "—"
        bean_rows.append(f"""
      <tr>
        <td>{e(bean)}</td>
        <td><strong>{int(values["batches"])}</strong></td>
        <td>{green:.1f}g</td>
        <td>{roasted:.1f}g</td>
        <td>{yield_text}</td>
      </tr>""")

    for idx, roast in enumerate(sorted(roasts, key=lambda r: (r.date, r.slug), reverse=True)):
        d = datetime.strptime(roast.date, "%Y-%m-%d") if roast.date else None
        month = d.strftime("%b").upper() if d else ""
        day = d.strftime("%d") if d else ""
        year = d.strftime("%Y") if d else ""
        latest = ' <small style="font-size:0.7rem; background:#e8f4f0; color:#2D4A3E; padding:1px 8px; border-radius:3px;">最新</small>' if idx == 0 else ""
        batch_yields = [b.yield_pct for b in roast.batches if b.yield_pct is not None]
        y_text = f"{sum(batch_yields) / len(batch_yields):.1f}%" if batch_yields else "—"
        cards.append(f"""
<a class="session-card" href="{e(roast.slug)}.html">
  <div class="session-date"><div class="d-month">{month}</div><div class="d-day">{day}</div><div class="d-year">{year}</div></div>
  <div class="session-divider"></div>
  <div class="session-info">
    <div class="session-title">{e(roast.bean or roast.slug)}{latest}</div>
    <div class="session-beans">{e(roast.purpose or '焙煎ログ')}　｜　狙い：{e(roast.target or '未記録')}</div>
    <div class="session-metrics">
      <div class="metric">バッチ数：<span>{len(roast.batches)}</span></div>
      <div class="metric">平均歩留まり：<span>{y_text}</span></div>
    </div>
  </div>
  <div class="arrow">›</div>
</a>""")
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Silver Tree — 焙煎プロファイル 記録一覧</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{ font-family: "Hiragino Mincho ProN", "Yu Mincho", Georgia, serif; background:#F8F4EE; color:#1C1C1C; max-width:920px; margin:0 auto; padding:48px 20px; }}
    h1 {{ font-size:1.35rem; font-weight:normal; color:#2D4A3E; border-bottom:1px solid #D4C5A9; padding-bottom:12px; margin-bottom:8px; }}
    .subtitle {{ color:#6B4226; font-size:.82rem; margin-bottom:40px; }}
    .stats-row {{ display:flex; gap:12px; margin-bottom:40px; flex-wrap:wrap; }}
    .stat-card {{ background:white; border-radius:8px; padding:16px 20px; box-shadow:0 1px 4px rgba(0,0,0,.07); flex:1; min-width:130px; text-align:center; }}
    .s-label {{ font-size:.72rem; color:#6B4226; margin-bottom:5px; }}
    .s-value {{ font-size:1.6rem; font-weight:bold; color:#2D4A3E; }}
    .section-header {{ font-size:.8rem; color:#888; letter-spacing:.1em; text-transform:uppercase; margin-bottom:16px; padding-bottom:6px; border-bottom:1px solid #E8E0D4; }}
    .session-card {{ background:white; border-radius:8px; padding:22px 24px; margin-bottom:12px; box-shadow:0 1px 4px rgba(0,0,0,.07); display:flex; align-items:flex-start; gap:20px; text-decoration:none; color:inherit; }}
    .session-card:hover {{ box-shadow:0 3px 12px rgba(0,0,0,.12); transform:translateY(-1px); }}
    .session-date {{ min-width:90px; text-align:center; }}
    .d-month {{ font-size:.72rem; color:#888; letter-spacing:.05em; }}
    .d-day {{ font-size:1.8rem; font-weight:bold; color:#2D4A3E; line-height:1.1; }}
    .d-year {{ font-size:.7rem; color:#bbb; }}
    .session-divider {{ width:1px; background:#F0E8DC; align-self:stretch; min-height:60px; }}
    .session-info {{ flex:1; }}
    .session-title {{ font-size:.95rem; color:#1C1C1C; margin-bottom:6px; font-weight:normal; }}
    .session-beans {{ font-size:.78rem; color:#6B4226; margin-bottom:10px; }}
    .session-metrics {{ display:flex; gap:16px; flex-wrap:wrap; }}
    .metric {{ font-size:.76rem; color:#666; }}
    .metric span {{ color:#2D4A3E; font-weight:600; }}
    .arrow {{ font-size:1.2rem; color:#D4C5A9; align-self:center; padding-left:8px; }}
    table {{ width:100%; border-collapse:collapse; overflow:hidden; background:white; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,.07); font-size:.86rem; margin-bottom:36px; }}
    th {{ background:#2D4A3E; color:white; padding:10px 12px; text-align:left; font-weight:normal; font-size:.78rem; }}
    td {{ padding:10px 12px; border-bottom:1px solid #F8F4EE; vertical-align:top; }}
    tr:last-child td {{ border-bottom:none; }}
    footer {{ text-align:center; color:#D4C5A9; font-size:.73rem; margin-top:56px; }}
  </style>
</head>
<body>
<h1>Silver Tree Coffee Roaster — 焙煎プロファイル記録</h1>
<p class="subtitle">roast-logs/*.md から自動生成　｜　roast-profiles/</p>
<div class="stats-row">
  <div class="stat-card"><div class="s-label">記録セッション数</div><div class="s-value">{len(roasts)}</div></div>
  <div class="stat-card"><div class="s-label">総バッチ数</div><div class="s-value">{total_batches}</div></div>
  <div class="stat-card"><div class="s-label">平均歩留まり</div><div class="s-value">{avg_yield:.1f}%</div></div>
  <div class="stat-card"><div class="s-label">最終記録</div><div class="s-value" style="font-size:1.1rem;">{e(latest_date)}</div></div>
</div>
<div class="stats-row">
  <div class="stat-card"><div class="s-label">生豆合計</div><div class="s-value">{total_green:.1f}g</div></div>
  <div class="stat-card"><div class="s-label">焙煎後合計</div><div class="s-value">{total_roasted:.1f}g</div></div>
  <div class="stat-card"><div class="s-label">重量減少</div><div class="s-value">{(total_green - total_roasted):.1f}g</div></div>
  <div class="stat-card"><div class="s-label">生成</div><div class="s-value" style="font-size:1.1rem;">AUTO</div></div>
</div>
<div class="section-header">豆別集計</div>
<table>
  <thead><tr><th>豆</th><th>バッチ</th><th>生豆合計</th><th>焙煎後合計</th><th>平均歩留まり</th></tr></thead>
  <tbody>{''.join(bean_rows)}</tbody>
</table>
<div class="section-header">セッション一覧 — 新しい順</div>
{''.join(cards)}
<footer>Silver Tree Coffee Roaster — generated from roast-logs</footer>
</body>
</html>
"""


def collect_inputs(input_paths: list[str] | None) -> list[Path]:
    if input_paths:
        return [Path(p) if Path(p).is_absolute() else ROOT / p for p in input_paths]
    return sorted(ROAST_LOG_DIR.glob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate roast profile HTML from roast-logs/*.md")
    parser.add_argument("inputs", nargs="*", help="Markdown files. Default: all roast-logs/*.md")
    parser.add_argument("--write", action="store_true", help="Write HTML files into roast-profiles/")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing profile HTML files")
    parser.add_argument("--index", action="store_true", help="Regenerate roast-profiles/index.html")
    parser.add_argument("--out-dir", default=str(PROFILE_DIR), help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    roasts = [parse_log(path) for path in collect_inputs(args.inputs)]
    for roast in roasts:
        if not roast.batches:
            print(f"skip: {roast.path} has no parseable batch")
            continue
        target = out_dir / f"{roast.slug}.html"
        if args.write:
            if target.exists() and not args.overwrite:
                print(f"exists: {target} (use --overwrite)")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_profile(roast), encoding="utf-8")
            print(f"wrote: {target}")
        else:
            print(f"ready: {roast.path.name} -> {target.name} ({len(roast.batches)} batches)")

    if args.index:
        if not args.write:
            print("index: dry-run only (add --write to update index.html)")
        else:
            out_dir.mkdir(parents=True, exist_ok=True)
            index_path = out_dir / "index.html"
            if index_path.exists() and not args.overwrite:
                print(f"exists: {index_path} (use --overwrite)")
            else:
                index_path.write_text(render_index([r for r in roasts if r.batches]), encoding="utf-8")
                print(f"wrote: {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
