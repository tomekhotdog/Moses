"""Textual dashboard for a live Moses loop campaign.

`MosesLoopApp` polls `loop_watch.read_state` on a timer and renders the campaign:
header stats, score sparkline, an iterations table, the weakest-commandment
breakdown, the latest diff, and a live log tail. On completion it shows a summary
screen. Strictly read-only over the ledger; the supervised subprocess (if any) is
terminated by the caller.

Render logic is split into pure module functions (`stats_text`, `breakdown_text`,
`bar`) so it is unit-testable without an event loop.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Log, Static

from .loop_watch import CampaignState, read_log, read_state


def bar(score: float, width: int = 20) -> str:
    filled = int(round(max(0.0, min(100.0, score)) / 100 * width))
    return "█" * filled + "·" * (width - filled)


def stats_text(s: CampaignState, max_iterations: int) -> str:
    if not s.exists:
        return "waiting for campaign…"
    done = len(s.rows)
    gain = s.total_gain
    sign = "+" if gain >= 0 else ""
    final = s.final_score
    return (
        f"baseline {s.baseline_score} {s.baseline_grade or ''}    "
        f"best {s.best_score} {s.best_grade or ''}    "
        f"iter {done}/{max_iterations}\n"
        f"Score {s.sparkline}  {s.baseline_score}→{final} ({sign}{gain})"
    )


def breakdown_text(s: CampaignState) -> str:
    if not s.weakest_rules:
        return "no verdict yet…"
    lines = ["[b]Weakest commandments[/b]", ""]
    for r in s.weakest_rules:
        lines.append(f"C{r.number:<2} {bar(r.score)} {r.score:5.1f}  {r.name[:20]}")
    return "\n".join(lines)


class SummaryScreen(Screen):
    BINDINGS = [("q", "app.quit", "Quit")]

    def __init__(self, state: CampaignState) -> None:
        super().__init__()
        self._summary = state.summary
        self._spark = state.sparkline

    def compose(self) -> ComposeResult:
        s = self._summary
        body = (
            "[b]Campaign complete[/b]\n\n"
            f"baseline   {s.baseline_score}\n"
            f"final      {s.final_score}\n"
            f"best       {s.best_score}\n"
            f"total gain {s.total_gain:+}\n"
            f"iterations {s.iterations} ({s.improving} up, {s.regressing} down)\n"
            f"trajectory {self._spark}\n\n"
            "[dim]press q to quit[/dim]"
        )
        yield Header()
        yield Static(body, id="summary")
        yield Footer()


class MosesLoopApp(App):
    CSS = """
    #stats { height: 4; padding: 0 1; border-bottom: solid $accent; }
    #middle { height: 1fr; }
    #left { width: 2fr; }
    #right { width: 1fr; border-left: solid $accent; }
    #iterations { height: 2fr; }
    #diff { height: 1fr; padding: 0 1; }
    #breakdown { padding: 0 1; }
    #log { height: 10; border-top: solid $accent; }
    """
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("up", "scroll_log(-1)", "Scroll log"),
        ("down", "scroll_log(1)", "Scroll log"),
    ]

    def __init__(self, *, state_dir, max_iterations: int, process=None, poll: float = 0.7):
        super().__init__()
        self._state_dir = Path(state_dir)
        self._max_iterations = max_iterations
        self._process = process
        self._poll = poll
        self._log_seen = 0
        self._finished = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="stats")
        with Horizontal(id="middle"):
            with Vertical(id="left"):
                yield DataTable(id="iterations")
                yield Static(id="diff")
            with Vertical(id="right"):
                yield Static(id="breakdown")
        yield Log(id="log", highlight=False)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#iterations", DataTable)
        table.add_columns("#", "Cmd", "Before", "After", "ΔViol", "")
        self.refresh_state()
        self.set_interval(self._poll, self.refresh_state)

    def refresh_state(self) -> None:
        s = read_state(self._state_dir)
        self.query_one("#stats", Static).update(stats_text(s, self._max_iterations))
        self._render_table(s)
        self.query_one("#breakdown", Static).update(breakdown_text(s))
        self.query_one("#diff", Static).update(
            ("[b]Last change[/b]\n" + s.last_diffstat) if s.last_diffstat else ""
        )
        self._render_log()
        if not self._finished and self._process is not None and self._process.poll() is not None:
            self._finished = True
            self.push_screen(SummaryScreen(s))

    def _render_table(self, s: CampaignState) -> None:
        table = self.query_one("#iterations", DataTable)
        table.clear()
        for r in s.rows:
            mark = "revert" if r.regression else "✓"
            if r.violations_after is None or r.violations_before is None:
                dv = ""
            else:
                dv = f"{r.violations_after - r.violations_before:+d}"
            table.add_row(str(r.iteration), r.commandment,
                          str(r.score_before), str(r.score_after), dv, mark)

    def _render_log(self) -> None:
        lines = read_log(self._state_dir)
        log = self.query_one("#log", Log)
        for line in lines[self._log_seen:]:
            log.write_line(line)
        self._log_seen = len(lines)

    def action_scroll_log(self, delta: int) -> None:
        log = self.query_one("#log", Log)
        log.scroll_relative(y=delta)
