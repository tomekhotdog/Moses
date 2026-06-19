"""Standalone, self-contained HTML report (minimal-brutalism + pastel)."""

from __future__ import annotations

import html as _html

from ..models import Verdict
from ..prompts import hint_for

_GRADE_BG = {
    "A": "#bde8c4",
    "B": "#cdeac0",
    "C": "#fdf6b2",
    "D": "#fde2c4",
    "E": "#f8c9c4",
    "F": "#f4b6b0",
}

_CSS = """
:root { --ink:#1a1a1a; --line:#1a1a1a; --bg:#faf7f2; }
* { box-sizing: border-box; }
body { font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  background: var(--bg); color: var(--ink); margin: 0; padding: 2rem; line-height: 1.5; }
.wrap { max-width: 980px; margin: 0 auto; }
.hero { border: 3px solid var(--line); padding: 1.5rem; margin-bottom: 1.5rem; }
.hero h1 { margin: 0 0 .5rem; letter-spacing: .3em; font-size: 1rem; }
.score { font-size: 3.5rem; font-weight: 700; }
.grade { display: inline-block; padding: .2rem 1rem; border: 3px solid var(--line);
  font-size: 2rem; font-weight: 700; margin-left: 1rem; }
.meta { font-size: .8rem; opacity: .7; margin-top: .5rem; }
table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
th, td { border: 1px solid var(--line); padding: .4rem .6rem; text-align: left; font-size: .85rem; }
th { background: #efe9df; }
td.num, td.r { text-align: right; }
.bar { height: 10px; border: 1px solid var(--line); background: #fff; }
.bar > span { display: block; height: 100%; background: #9ad0c2; }
.sec { border: 3px solid var(--line); padding: 1rem 1.25rem; margin-bottom: 1.5rem; }
.sec h2 { margin: 0 0 .75rem; font-size: 1rem; letter-spacing: .15em; }
.viol { font-size: .78rem; opacity: .85; }
.pill { display:inline-block; padding:0 .4rem; border:1px solid var(--line); margin:0 .2rem .2rem 0; font-size:.75rem;}
"""


def _esc(s) -> str:
    return _html.escape(str(s))


def _bar(score: float) -> str:
    pct = max(0.0, min(100.0, score))
    return f'<div class="bar"><span style="width:{pct:.0f}%"></span></div>'


def render_html(verdict: Verdict) -> str:
    grade_bg = _GRADE_BG.get(verdict.grade, "#eee")
    ov = verdict.overview
    meta = verdict.meta

    rows = []
    for c in verdict.commandments:
        if c.status == "not_measured":
            continue
        metric = "—" if c.metric is None else f"{c.metric:.2f}"
        rows.append(
            f"<tr><td class='num'>{c.number}</td>"
            f"<td>{_esc(c.name)}<div class='viol'>{_esc(hint_for(c.number))}</div></td>"
            f"<td class='num'>{c.weight}</td>"
            f"<td class='num'>{metric}</td>"
            f"<td class='r'>{c.score_contribution:.1f}</td>"
            f"<td>{_bar(c.score_contribution)}</td>"
            f"<td>{_esc(c.status)}</td></tr>"
        )

    hotspot_rows = []
    for h in verdict.hotspots:
        hits = "".join(
            f"<span class='pill'>#{n}×{cnt}</span>"
            for n, cnt in h.get("commandment_hits", {}).items()
        )
        hotspot_rows.append(
            f"<tr><td>{_esc(h['file'])}</td>"
            f"<td class='num'>{h['severity']:.1f}</td>"
            f"<td>{hits}</td></tr>"
        )

    hotspot_section = ""
    if hotspot_rows:
        hotspot_section = (
            "<div class='sec'><h2>HOTSPOTS</h2><table>"
            "<tr><th>File</th><th>Severity</th><th>Rules hit</th></tr>"
            + "".join(hotspot_rows)
            + "</table></div>"
        )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moses Report — Grade {verdict.grade}</title>
<style>{_CSS}</style></head>
<body><div class="wrap">
<div class="hero" style="background:{grade_bg}">
  <h1>M O S E S</h1>
  <span class="score">{verdict.score:.1f}</span>
  <span class="grade">{verdict.grade}</span>
  <div class="meta">{ov.get('file_count', 0)} files · {ov.get('loc', 0)} LOC ·
    v{_esc(meta.get('tool_version',''))} · {_esc(meta.get('timestamp',''))}</div>
</div>
<div class="sec"><h2>COMMANDMENTS</h2>
<table>
<tr><th>#</th><th>Commandment</th><th>W</th><th>Metric</th><th>Score</th><th></th><th>Status</th></tr>
{''.join(rows)}
</table></div>
{hotspot_section}
</div></body></html>
"""
