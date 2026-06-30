"""Command-line interface for Moses.

Commands:
  moses judge <path> ...        run the scorer, print/emit a Verdict
  moses prompt <N>              print the per-Commandment refactoring brief
  moses loop init|run|check|status ...
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import click

from . import __version__
from .config import Config
from .engine import run as engine_run

# Exit codes by Grade: 0 for A/B/C, 1 for D/E, 2 for F.
_EXIT_BY_GRADE = {"A": 0, "B": 0, "C": 0, "D": 1, "E": 1, "F": 2}


@click.group()
@click.version_option(__version__, "-V", "--version", prog_name="moses")
def main() -> None:
    """Moses — a code quality oracle for Python."""


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--config", "config_file", type=click.Path(exists=True), help="YAML config file.")
@click.option("--enable", "enable", multiple=True, type=int, help="Enable Commandment N.")
@click.option("--disable", "disable", multiple=True, type=int, help="Disable Commandment N.")
@click.option("--exclude", "exclude", multiple=True, help="Glob to exclude from the scan.")
@click.option("--json", "json_out", type=click.Path(), help="Write Verdict JSON here.")
@click.option("--html", "html_out", type=click.Path(), help="Write HTML report here.")
@click.option("--deep", is_flag=True, help="Enable opt-in slow rules (mutation #20).")
@click.option("--quiet", is_flag=True, help="Suppress terminal report.")
def judge(
    path: str,
    config_file: str | None,
    enable: tuple[int, ...],
    disable: tuple[int, ...],
    exclude: tuple[str, ...],
    json_out: str | None,
    html_out: str | None,
    deep: bool,
    quiet: bool,
) -> None:
    """Judge the source tree at PATH and report a Score and Grade."""
    if config_file:
        config = Config.from_file(config_file)
    else:
        config = Config()
    config = config.with_overrides(
        enable=list(enable),
        disable=list(disable),
        exclude=list(exclude),
        deep=deep or None,
    )

    verdict = engine_run(path, config)

    if json_out:
        Path(json_out).write_text(
            json.dumps(verdict.to_dict(), indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )
    if html_out:
        from .report.html import render_html

        Path(html_out).write_text(render_html(verdict), encoding="utf-8")

    if not quiet:
        from .report.terminal import render_terminal

        render_terminal(verdict)

    sys.exit(_EXIT_BY_GRADE.get(verdict.grade, 2))


@main.command()
@click.argument("number", type=int)
def prompt(number: int) -> None:
    """Print the curated refactoring brief for Commandment NUMBER."""
    from .prompts import prompt_for

    click.echo(prompt_for(number))


@main.group()
def loop() -> None:
    """Autonomous improvement loop (RALPH harness)."""


@loop.command("init")
@click.argument("target", type=click.Path(exists=True))
@click.option("--target-path", default="src/", help="Path within the repo to judge.")
@click.option("--branch", default=None, help="Branch name for the loop.")
@click.option("--in-place", is_flag=True, help="Commit onto the current branch.")
@click.option("--base-ref", default="HEAD", help="Base ref for the worktree.")
@click.option("--worktree", "worktree_path", default=None, help="Worktree path override.")
@click.option("--state-dir", "state_dir", default=".moses", help="State dir name.")
def loop_init_cmd(target, target_path, branch, in_place, base_ref, worktree_path, state_dir):
    """Initialise a loop campaign against TARGET repo."""
    from .loop_runner import loop_init

    result = loop_init(
        target=target,
        branch=branch,
        worktree_path=worktree_path,
        base_ref=base_ref,
        target_path=target_path,
        state_dir_name=state_dir,
        in_place=in_place,
    )
    click.echo(result)


@loop.command("run")
@click.option("--worktree", "worktree", required=True, type=click.Path(exists=True))
@click.option("--state-dir", "state_dir", default=".moses")
@click.option("--engine", default="auto", type=click.Choice(["auto", "claude", "codex"]))
@click.option("--max-iterations", default=10, type=int)
@click.option("--max-hours", default=0.0, type=float)
@click.option("--cooldown", default=5, type=int)
def loop_run_cmd(worktree, state_dir, engine, max_iterations, max_hours, cooldown):
    """Run the autonomous loop in WORKTREE."""
    from .loop_runner import loop_run

    code = loop_run(
        worktree=worktree,
        state_dir_name=state_dir,
        engine=engine,
        max_iterations=max_iterations,
        max_hours=max_hours,
        cooldown=cooldown,
    )
    sys.exit(code)


@loop.command("watch")
@click.argument("target", required=False, type=click.Path(exists=True))
@click.option("--worktree", "worktree", default=None, type=click.Path(),
              help="Existing campaign worktree (skip auto-init).")
@click.option("--target-path", default="src/", help="Path within the repo to judge.")
@click.option("--in-place", is_flag=True, help="Auto-init onto the current branch.")
@click.option("--state-dir", "state_dir", default=".moses", help="State dir name.")
@click.option("--engine", default="auto", type=click.Choice(["auto", "claude", "codex"]),
              help="Coding engine for each iteration.")
@click.option("--max-iterations", default=10, type=int, help="Max iterations to run.")
@click.option("--max-hours", default=0.0, type=float, help="Wall-clock budget (0 = unlimited).")
@click.option("--cooldown", default=5, type=int, help="Seconds to sleep between iterations.")
def loop_watch_cmd(target, worktree, target_path, in_place, state_dir, engine,
                   max_iterations, max_hours, cooldown):
    """Launch a campaign and watch it live in a terminal dashboard.

    Pass TARGET to auto-init a campaign (worktree mode unless --in-place), or
    --worktree to attach to an existing one.
    """
    from . import loop_runner
    from .loop_runner import LoopError, default_worktree_path, loop_init, _resolve_state

    if worktree is None:
        if target is None:
            raise SystemExit("provide TARGET (to auto-init) or --worktree (existing campaign)")
        wt = target if in_place else default_worktree_path(target)
        paths = _resolve_state(wt, state_dir)
        if not paths.campaign.exists():
            try:
                click.echo(loop_init(
                    target=target, target_path=target_path,
                    state_dir_name=state_dir, in_place=in_place,
                ))
            except LoopError as exc:
                raise SystemExit(str(exc))
        worktree = str(paths.worktree)

    paths = _resolve_state(worktree, state_dir)
    if not paths.campaign.exists():
        raise SystemExit(f"no campaign at {paths.campaign}; run `moses loop init` first")

    try:
        from .loop_tui import MosesLoopApp
    except ImportError:
        raise SystemExit("The loop dashboard needs Textual:\n  uv pip install 'moses[tui]'")

    proc = loop_runner.loop_spawn(
        worktree=worktree, state_dir_name=state_dir, engine=engine,
        max_iterations=max_iterations, max_hours=max_hours, cooldown=cooldown,
    )
    try:
        MosesLoopApp(state_dir=paths.state_dir, max_iterations=max_iterations,
                     process=proc).run()
    finally:
        # Always reap the child to avoid a zombie — terminate first only if it is
        # still running; then wait() regardless of whether it already exited.
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        else:
            proc.wait()


@loop.command("check")
@click.option("--worktree", "worktree", required=True, type=click.Path(exists=True))
@click.option("--state-dir", "state_dir", default=".moses")
def loop_check_cmd(worktree, state_dir):
    """Validate campaign.json against git and verdicts."""
    from .loop_runner import loop_check

    sys.exit(loop_check(worktree=worktree, state_dir_name=state_dir))


@loop.command("status")
@click.option("--worktree", "worktree", required=True, type=click.Path(exists=True))
@click.option("--state-dir", "state_dir", default=".moses")
def loop_status_cmd(worktree, state_dir):
    """Print a terse progress summary."""
    from .loop_runner import loop_status

    click.echo(loop_status(worktree=worktree, state_dir_name=state_dir))


if __name__ == "__main__":
    main()
