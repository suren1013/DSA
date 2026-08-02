"""`push` subcommand: mark a problem solved, regenerate, and push."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

from . import config
from .utils import error, git_push, info, run_command, success, title_case_from_slug, today_iso, warn


def register_parser(subparsers) -> None:
    """Register the `push` subcommand parser."""
    parser = subparsers.add_parser(
        "push",
        aliases=["sp"],
        help="Mark a problem solved, regenerate dashboards, and push to GitHub.",
    )
    parser.set_defaults(func=run)


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def _load_metadata(meta_path: Path) -> Optional[dict]:
    """Safely load a metadata.json file, returning None on failure."""
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _find_solving_problems() -> list[tuple[Path, dict]]:
    """Return (metadata_path, metadata) for every problem with status 'Solving'."""
    solving: list[tuple[Path, dict]] = []
    if not config.PROBLEMS_DIR.exists():
        return solving

    for meta_path in sorted(config.PROBLEMS_DIR.glob("*/*/metadata.json")):
        data = _load_metadata(meta_path)
        if data and data.get("status") == config.STATUS_SOLVING:
            solving.append((meta_path, data))
    return solving


def _select_problem(problems: list[tuple[Path, dict]]) -> tuple[Path, dict]:
    """Let the user choose a problem when multiple are 'Solving'."""
    print("Multiple problems are marked 'Solving'. Which did you solve?")
    print()
    for i, (_, data) in enumerate(problems, 1):
        title = data.get("title", "?")
        topic = data.get("topic", "?")
        print(f"  {i}. [{topic}] {title}")
    print()
    print("  0. Cancel")
    print()

    while True:
        try:
            choice = input("Enter a number: ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit("Aborted by user.")

        if choice == "0":
            raise SystemExit("Cancelled.")
        try:
            idx = int(choice)
        except ValueError:
            warn(f"'{choice}' is not a number. Try again.")
            continue
        if 1 <= idx <= len(problems):
            return problems[idx - 1]
        warn(f"Number out of range (1–{len(problems)}). Try again.")


def _mark_solved(meta_path: Path, data: dict) -> None:
    """Update status -> Solved and set solved date in the metadata file."""
    data["status"] = config.STATUS_SOLVED
    data["solved"] = today_iso()
    meta_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------

def _step_validate(problems_root: Path) -> None:
    """Step 1: run validation; abort on failure."""
    info("Step 1/7: Validating repository…")
    run_command(
        ["python", str(config.VALIDATE_CMD[0])],
        cwd=config.REPO_ROOT,
        description="Validate structure & metadata",
    )
    success("✔ Validation passed")


def _step_mark_solved() -> Optional[dict]:
    """Step 2: mark a 'Solving' problem as Solved."""
    info("Step 2/7: Checking for problems marked 'Solving'…")
    solving = _find_solving_problems()

    if not solving:
        warn("No problems with status 'Solving' — skipping solve step.")
        return None

    if len(solving) > 1:
        meta_path, data = _select_problem(solving)
    else:
        meta_path, data = solving[0]
        title = data.get("title", "?")
        # Auto-confirm when exactly one problem is Solving.
        print(f"  Auto-selected: {title}")
        try:
            confirm = input("  Mark as solved? [Y/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            confirm = "y"
        if confirm in ("n", "no"):
            warn("Skipped marking problem as solved.")
            return None

    _mark_solved(meta_path, data)
    topic = data.get("topic", "?")
    title = data.get("title", "?")
    success(f"✔ Marked problem solved: [{topic}] {title}")
    return {"topic": topic, "slug": data.get("slug", "")}


def _step_regenerate() -> None:
    """Step 3: regenerate dashboard, site data, and README."""
    info("Step 3/7: Regenerating dashboard, site, and README…")
    run_command(
        ["python", "scripts/generate_dashboard.py"], config.REPO_ROOT,
        "Generate dashboard/stats.json",
    )
    run_command(
        ["python", "scripts/build_site.py"], config.REPO_ROOT,
        "Build site/data/stats.json",
    )
    run_command(
        ["python", "scripts/generate_readme.py"], config.REPO_ROOT,
        "Update README.md",
    )
    success("✔ Dashboard regenerated")
    success("✔ README updated")


def _commit_message(solved: Optional[dict]) -> str:
    """Build a conventional commit message, e.g. solve(arrays): Two Sum."""
    if solved:
        topic = solved.get("topic", "misc")
        slug = solved.get("slug", "")
        title = title_case_from_slug(slug) if slug else "Problem solved"
        return f"solve({topic}): {title}"
    return "chore: regenerate dashboard and README"


def _step_git(solved: Optional[dict]) -> None:
    """Steps 4-7: git add, commit, push."""
    root = config.REPO_ROOT

    info("Step 4/7: Staging all changes…")
    run_command(["git", "add", "."], root, "Staging files")
    success("✔ Changes staged")

    message = _commit_message(solved)

    info("Step 5/7: Creating commit…")
    run_command(
        ["git", "commit", "-m", message],
        root,
        f"Commit: {message}",
    )
    success("✔ Commit created")

    info("Step 6/7: Pushing to GitHub…")
    git_push(root)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace) -> int:
    """Execute the `push` command pipeline."""
    print()
    info("Starting Solve & Push pipeline…")
    print()

    try:
        _step_validate(config.REPO_ROOT)
        solved = _step_mark_solved()
        _step_regenerate()
        _step_git(solved)
    except SystemExit as exc:
        if exc.code:
            error(f"\nPipeline aborted: {exc.code}")
        else:
            error("\nPipeline aborted.")
        return exc.code if isinstance(exc.code, int) else 1

    print()
    success("✔ All done! Solution pushed to GitHub.")
    print()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="cli push")
    args = parser.parse_args()
    raise SystemExit(run(args))