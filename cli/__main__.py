"""CLI entrypoint: `python -m cli` exposes the `new` and `push` subcommands."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from . import new_problem, reset, solve_push
from .utils import error, info


def build_parser() -> argparse.ArgumentParser:
    """Build the root argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="python -m cli",
        description="DSA Tracker CLI — manage problems and push solutions.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        metavar="<command>",
        required=True,
    )

    # Register subcommands here. Future commands (stats, search, revise,
    # export) just need a module with register_parser(subparsers).
    new_problem.register_parser(subparsers)
    solve_push.register_parser(subparsers)
    reset.register_parser(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI with the given argv (defaults to sys.argv[1:])."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help(sys.stderr)
        return 2

    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        error("Interrupted. Exiting.")
        return 130
    except Exception as exc:  # pragma: no cover - defensive fallback
        error(f"Unexpected error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())