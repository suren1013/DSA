"""`reset` subcommand: restore the repository to a fresh state.

Deletes all problem folders (keeping topic folders), regenerates the
dashboard/site/README, and optionally creates a git commit.

Safety: only removes user-created problem folders and generated statistics.
Never touches cli/, scripts/, .github/, templates/, docs/, site/assets/,
LICENSE, ROADMAP.md, or CONTRIBUTING.md.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import config
from .utils import error, git_push, info, run_command, success, warn


def register_parser(subparsers) -> None:
    """Register the `reset` subcommand parser."""
    parser = subparsers.add_parser(
        "reset",
        help="Delete all problems and regenerate dashboards (keeps infrastructure).",
    )
    parser.set_defaults(func=run)


# ---------------------------------------------------------------------------
# Safety helpers
# ---------------------------------------------------------------------------

def _confirm(prompt: str) -> bool:
    """Ask a yes/no question. Returns True only for y/yes."""
    try:
        answer = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer in ("y", "yes")


def _delete_problem_folders() -> list[str]:
    """Delete every problem subfolder under problems/, keeping topic folders.

    Returns a list of relative paths (e.g. 'arrays/two-sum') of deleted folders.
    """
    deleted: list[str] = []
    if not config.PROBLEMS_DIR.exists():
        return deleted

    for topic_dir in sorted(config.PROBLEMS_DIR.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("."):
            continue
        for problem_dir in sorted(topic_dir.iterdir()):
            if not problem_dir.is_dir() or problem_dir.name.startswith("."):
                continue
            # Validate the path is inside problems/ before deleting.
            try:
                problem_dir.relative_to(config.PROBLEMS_DIR)
            except ValueError:
                error(f"Refusing to delete outside problems/: {problem_dir}")
                continue
            rel_path = str(problem_dir.relative_to(config.PROBLEMS_DIR)).replace("\\", "/")
            shutil.rmtree(problem_dir)
            deleted.append(rel_path)

    return deleted


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------

def _step_warning() -> bool:
    """Print the warning and ask for confirmation. Returns True to proceed."""
    warn("⚠ This will permanently remove ALL tracked problems.")
    print()
    print("The following WILL be deleted:")
    print("  - problems/*")
    print("  - generated dashboard statistics")
    print("  - generated site data")
    print("  - generated README sections")
    print()
    print("The following will NOT be deleted:")
    print("  - scripts/")
    print("  - cli/")
    print("  - .github/")
    print("  - templates/")
    print("  - documentation")
    print("  - workflows")
    print("  - project configuration")
    print()
    return _confirm("Continue? (y/N) ")


def _step_delete_problems() -> None:
    """Step 1: delete all problem folders."""
    info("Step 1/3: Deleting problem folders…")
    deleted = _delete_problem_folders()
    count = len(deleted)
    success(f"✔ Deleted {count} problem folder{'s' if count != 1 else ''}")
    if deleted:
        for path in deleted:
            print(f"  • {path}")


def _step_regenerate() -> None:
    """Step 2: regenerate dashboard, site data, and README."""
    info("Step 2/3: Regenerating dashboard, site, and README…")
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
    success("✔ README regenerated")


def _step_git() -> None:
    """Step 3: optionally create a git commit and push."""
    info("Step 3/3: Git integration…")
    if not _confirm("Create a git commit? (y/N) "):
        warn("Skipped git commit — repository left modified but uncommitted.")
        return

    root = config.REPO_ROOT
    run_command(["git", "add", "."], root, "Staging all changes")
    run_command(
        ["git", "commit", "-m", "chore: reset repository"],
        root,
        "Commit: chore: reset repository",
    )
    success("✔ Commit created")

    # Use the shared git push helper (fetch + rebase + retry).
    try:
        git_push(root)
    except SystemExit:
        warn("Push failed — commit was created locally.")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace) -> int:
    """Execute the `reset` command pipeline."""
    print()
    info("Starting repository reset…")
    print()

    if not _step_warning():
        warn("Reset aborted — no changes were made.")
        return 0

    try:
        _step_delete_problems()
        _step_regenerate()
        _step_git()
    except SystemExit as exc:
        error(f"\nReset aborted: {exc.code}")
        return exc.code if isinstance(exc.code, int) else 1

    print()
    success("✔ Repository reset complete")
    print()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="cli reset")
    args = parser.parse_args()
    raise SystemExit(run(args))