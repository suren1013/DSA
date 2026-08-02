"""`new` subcommand: scaffold a new DSA problem folder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config
from .templates import metadata_template, notes_template, solution_template
from .utils import error, info, open_in_vscode, success, to_slug, today_iso, warn


def register_parser(subparsers) -> None:
    """Register the `new` subcommand parser."""
    parser = subparsers.add_parser(
        "new",
        aliases=["np"],
        help="Create a new problem folder (Solution.java, metadata.json, notes.md).",
    )
    parser.add_argument("name", help="Problem name, e.g. \"Two Sum\"")
    parser.add_argument("topic", help="Topic slug, e.g. arrays")
    parser.add_argument(
        "source",
        nargs="?",
        default=config.DEFAULT_SOURCE,
        help="Source platform (default: custom)",
    )
    parser.set_defaults(func=run)


def _write_if_missing(path: Path, content: str) -> bool:
    """Write a file only if it does not already exist. Returns True if created."""
    if path.exists():
        warn(f"Skipped existing file: {path.relative_to(config.REPO_ROOT)}")
        return False
    path.write_text(content, encoding="utf-8")
    return True


def run(args: argparse.Namespace) -> int:
    """Execute the `new` command."""
    title = args.name.strip()
    topic = args.topic.strip().lower()
    source = args.source.strip().lower() or config.DEFAULT_SOURCE

    if not title:
        error("Problem name cannot be empty.")
        return 1
    if not topic:
        error("Topic cannot be empty.")
        return 1

    slug = to_slug(title)
    if not slug:
        error(f"Could not derive a slug from: {args.name!r}")
        return 1

    problem_dir = config.PROBLEMS_DIR / topic / slug

    # Create the folder structure (parent topic folder may already exist).
    problem_dir.mkdir(parents=True, exist_ok=True)

    info(f"Creating problem: {topic}/{slug}")

    created = today_iso()
    metadata = metadata_template(
        title=title,
        slug=slug,
        topic=topic,
        source=source,
        status=config.STATUS_SOLVING,
        language=config.DEFAULT_LANGUAGE,
        difficulty=config.DIFFICULTY_UNKNOWN,
        created=created,
    )

    solution_path = problem_dir / config.SOLUTION_FILENAME
    metadata_path = problem_dir / config.METADATA_FILENAME
    notes_path = problem_dir / config.NOTES_FILENAME

    _write_if_missing(solution_path, solution_template())
    _write_if_missing(metadata_path, metadata)
    _write_if_missing(notes_path, notes_template())

    # Friendly summary output.
    print()
    success(f"✔ Created {problem_dir.relative_to(config.REPO_ROOT)}")
    print(f"    {config.SOLUTION_FILENAME}")
    print(f"    {config.METADATA_FILENAME}")
    print(f"    {config.NOTES_FILENAME}")
    print()

    # Automatically open Solution.java in VS Code (best-effort).
    open_in_vscode(solution_path)

    return 0


if __name__ == "__main__":
    # Allow direct execution for testing: python -m cli.new_problem <args>
    parser = argparse.ArgumentParser(prog="cli new")
    parser.add_argument("name")
    parser.add_argument("topic")
    parser.add_argument("source", nargs="?", default=config.DEFAULT_SOURCE)
    args = parser.parse_args(sys.argv[1:] if len(sys.argv) > 1 else [])
    parser.set_defaults(func=run)
    raise SystemExit(run(args))