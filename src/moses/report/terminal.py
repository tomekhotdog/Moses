"""Rich-based terminal report for a Verdict."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..models import Verdict

_GRADE_COLOR = {
    "A": "bold green",
    "B": "green",
    "C": "yellow",
    "D": "orange3",
    "E": "red",
    "F": "bold red",
}

_STATUS_STYLE = {
    "measured": "white",
    "not_measured": "dim",
    "error": "red",
}


def render_terminal(verdict: Verdict, console: Console | None = None) -> None:
    console = console or Console()
    color = _GRADE_COLOR.get(verdict.grade, "white")

    header = Text()
    header.append(f"Score {verdict.score:.1f}/100", style="bold")
    header.append("   ")
    header.append(f"Grade {verdict.grade}", style=color)
    ov = verdict.overview
    sub = f"{ov.get('file_count', 0)} files · {ov.get('loc', 0)} LOC"
    console.print(Panel(header, title="MOSES", subtitle=sub, border_style=color))

    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("#", justify="right", width=3)
    table.add_column("Commandment")
    table.add_column("W", justify="right", width=3)
    table.add_column("Metric", justify="right", width=10)
    table.add_column("Score", justify="right", width=7)
    table.add_column("Status", width=12)

    for c in verdict.commandments:
        if c.status == "not_measured":
            continue
        metric = "—" if c.metric is None else f"{c.metric:.2f}"
        score_text = Text(f"{c.score_contribution:.1f}")
        if c.score_contribution >= 80:
            score_text.stylize("green")
        elif c.score_contribution >= 50:
            score_text.stylize("yellow")
        else:
            score_text.stylize("red")
        table.add_row(
            str(c.number),
            c.name,
            str(c.weight),
            metric,
            score_text,
            Text(c.status, style=_STATUS_STYLE.get(c.status, "white")),
        )
    console.print(table)

    if verdict.hotspots:
        hs = Table(title="Hotspots", show_header=True, header_style="bold red", expand=True)
        hs.add_column("File")
        hs.add_column("Severity", justify="right")
        hs.add_column("Rules hit")
        for h in verdict.hotspots[:10]:
            hits = ", ".join(f"#{n}" for n in h.get("commandment_hits", {}))
            hs.add_row(h["file"], f"{h['severity']:.1f}", hits)
        console.print(hs)
