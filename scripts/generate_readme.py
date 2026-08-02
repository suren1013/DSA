#!/usr/bin/env python3
"""
Generate or update the root README.md with auto-generated sections built from
scanned problem metadata.

The generator is **idempotent**: it only replaces the content between the
marker comments below, so manual content elsewhere in the README is preserved
no matter how many times the script runs.

    <!-- DSA:AUTO:START -->
    ... auto-generated content (replaced every run) ...
    <!-- DSA:AUTO:END -->

Generated sections:
  - Statistics summary
  - Topic-wise summary sections
  - Solved problems table
  - Recent activity section
  - Language breakdown section

Usage:
  python scripts/generate_readme.py
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Make sibling scanner.py importable regardless of CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scanner import Problem, scan_problems  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"

START_MARKER = "<!-- DSA:AUTO:START -->"
END_MARKER = "<!-- DSA:AUTO:END -->"

RECENT_ACTIVITY_LIMIT = 10


def _link(problem: Problem) -> str:
    """Markdown link to the problem's README if it exists, else the folder."""
    readme = ROOT / problem.path / "README.md"
    label = problem.title or problem.slug
    if readme.exists():
        return f"[{label}]({problem.path}/README.md)"
    return f"[{label}]({problem.path})"


def _or_dash(value: str) -> str:
    return value if value else "—"


def generate_stats(problems: list[Problem]) -> str:
    total = len(problems)
    solved = sum(1 for p in problems if p.is_solved)
    in_progress = sum(1 for p in problems if p.status == "in-progress")
    todo = sum(1 for p in problems if p.status == "todo")

    diff_counts = Counter(p.difficulty for p in problems)

    lines = [
        "## 📊 Statistics",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total problems | {total} |",
        f"| Solved | {solved} |",
        f"| In progress | {in_progress} |",
        f"| To do | {todo} |",
        f"| Easy | {diff_counts.get('easy', 0)} |",
        f"| Medium | {diff_counts.get('medium', 0)} |",
        f"| Hard | {diff_counts.get('hard', 0)} |",
    ]
    return "\n".join(lines)


def generate_topic_sections(problems: list[Problem]) -> str:
    if not problems:
        return "## 🗂️ Topics\n\n_No problems tracked yet._"

    by_topic: dict[str, list[Problem]] = defaultdict(list)
    for p in problems:
        by_topic[p.topic].append(p)

    lines = ["## 🗂️ Topics"]
    for topic in sorted(by_topic):
        items = by_topic[topic]
        lines.append("")
        lines.append(f"### {topic} ({len(items)})")
        lines.append("")
        lines.append("| Problem | Difficulty | Status | Time | Space | Source |")
        lines.append("|---------|-----------|--------|------|-------|--------|")
        for p in sorted(items, key=lambda x: x.title.lower()):
            lines.append(
                f"| {_link(p)} | {_or_dash(p.difficulty)} | "
                f"{_or_dash(p.status)} | {_or_dash(p.time_complexity)} | "
                f"{_or_dash(p.space_complexity)} | {_or_dash(p.platform)} |"
            )
    return "\n".join(lines)


def generate_solved_table(problems: list[Problem]) -> str:
    solved = [p for p in problems if p.is_solved]
    if not solved:
        return "## ✅ Solved Problems\n\n_No problems solved yet._"

    solved.sort(key=lambda p: (p.solved_date, p.title))

    lines = [
        "## ✅ Solved Problems",
        "",
        "| # | Problem | Topic | Difficulty | Time | Space | Source | Solved |",
        "|---|---------|-------|-----------|------|-------|--------|--------|",
    ]
    for i, p in enumerate(solved, 1):
        lines.append(
            f"| {i} | {_link(p)} | {p.topic} | {_or_dash(p.difficulty)} | "
            f"{_or_dash(p.time_complexity)} | {_or_dash(p.space_complexity)} | "
            f"{_or_dash(p.platform)} | {_or_dash(p.solved_date)} |"
        )
    return "\n".join(lines)


def generate_recent_activity(problems: list[Problem]) -> str:
    """Collect all attempts across problems, sort by date descending."""
    rows: list[tuple[str, str, str, str]] = []  # (date, problem, topic, outcome)
    for p in problems:
        for att in p.attempts:
            d = att.get("date", "")
            outcome = att.get("outcome", "")
            if d and outcome:
                rows.append((d, p.title or p.slug, p.topic, outcome))

    if not rows:
        return "## 🕐 Recent Activity\n\n_No attempts recorded yet._"

    rows.sort(key=lambda r: r[0], reverse=True)
    rows = rows[:RECENT_ACTIVITY_LIMIT]

    lines = [
        "## 🕐 Recent Activity",
        "",
        "| Date | Problem | Topic | Outcome |",
        "|------|---------|-------|---------|",
    ]
    for d, title, topic, outcome in rows:
        lines.append(f"| {d} | {title} | {topic} | {outcome} |")
    return "\n".join(lines)


def generate_language_breakdown(problems: list[Problem]) -> str:
    counts = Counter(p.language for p in problems)
    if not counts:
        return "## 💻 Language Breakdown\n\n_No problems tracked yet._"

    lines = [
        "## 💻 Language Breakdown",
        "",
        "| Language | Count |",
        "|----------|-------|",
    ]
    for lang, count in sorted(counts.items()):
        lines.append(f"| {lang} | {count} |")
    return "\n".join(lines)


def generate_content(problems: list[Problem]) -> str:
    """Assemble the full auto-generated block (including markers)."""
    sections = [
        START_MARKER,
        "<!-- Auto-generated by scripts/generate_readme.py — do not edit between markers. -->",
        generate_stats(problems),
        generate_topic_sections(problems),
        generate_solved_table(problems),
        generate_recent_activity(problems),
        generate_language_breakdown(problems),
        END_MARKER,
    ]
    return "\n\n".join(sections)


def update_readme(problems: list[Problem]) -> bool:
    """Replace content between markers in README.md. Returns True if changed."""
    content = generate_content(problems)

    if README_PATH.exists():
        text = README_PATH.read_text(encoding="utf-8")
        if START_MARKER in text and END_MARKER in text:
            pattern = re.compile(
                re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
                re.DOTALL,
            )
            new_text = pattern.sub(content, text)
        else:
            # Insert the auto-generated block before the Quick start section,
            # or append at the end if that section is not found.
            anchor = "## 🚀 Quick start"
            if anchor in text:
                new_text = text.replace(anchor, content + "\n\n---\n\n" + anchor, 1)
            else:
                new_text = text.rstrip() + "\n\n" + content + "\n"
    else:
        new_text = content + "\n"

    if new_text == (README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""):
        return False

    README_PATH.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    problems = scan_problems()
    changed = update_readme(problems)
    print(f"Scanned {len(problems)} problem(s).")
    if changed:
        print(f"Updated {README_PATH.relative_to(ROOT)}")
    else:
        print(f"No changes needed — {README_PATH.relative_to(ROOT)} is up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())