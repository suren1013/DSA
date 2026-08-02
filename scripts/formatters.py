#!/usr/bin/env python3
"""
Reusable Markdown formatting helpers for the DSA dashboard and README generator.

All functions return plain Markdown strings that can be composed together.
No project-specific logic lives here — these are generic primitives.
"""

from __future__ import annotations

FILL = "█"
EMPTY = "░"


def progress_bar(
    value: int,
    total: int,
    width: int = 20,
    show_percent: bool = True,
    show_count: bool = False,
) -> str:
    """Generate a Unicode progress bar.

    Example: progress_bar(3, 10, width=10) -> '███░░░░░░░ 30%'
    """
    if total <= 0:
        pct = 0.0
        filled = 0
    else:
        pct = min(value / total, 1.0)
        filled = round(pct * width)
    empty = width - filled
    bar = FILL * filled + EMPTY * empty
    parts = [bar]
    if show_percent:
        parts.append(f"{int(pct * 100)}%")
    if show_count:
        parts.append(f"({value}/{total})")
    return " ".join(parts)


def code_bar(
    value: int,
    total: int,
    width: int = 20,
    show_percent: bool = True,
    show_count: bool = False,
) -> str:
    """Like progress_bar but wrapped in backticks for monospace rendering."""
    return f"`{progress_bar(value, total, width, show_percent, show_count)}`"


def table(headers: list[str], rows: list[list[str]]) -> str:
    """Generate a Markdown table from headers and rows."""
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def dash_if_empty(value: str) -> str:
    """Return an em-dash placeholder if the value is empty."""
    return value if value else "—"


def pluralize(count: int, singular: str) -> str:
    """Return '1 day' or '3 days'."""
    return f"{count} {singular}{'s' if count != 1 else ''}"