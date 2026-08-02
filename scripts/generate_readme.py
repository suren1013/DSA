#!/usr/bin/env python3
"""
Generate or update the root README.md with a polished, auto-generated dashboard
built from scanned problem metadata and git history.

The generator is **idempotent**: it only replaces the content between the
marker comments below, so manual content elsewhere in the README is preserved
no matter how many times the script runs.

    <!-- DSA:AUTO:START -->
    ... auto-generated content (replaced every run) ...
    <!-- DSA:AUTO:END -->

Generated sections:
  - Overview with progress bars (solve rate, difficulty breakdown)
  - Streak & activity summary
  - Topic-wise progress sections
  - Solved problems table
  - Recent solves
  - Recent activity
  - Language breakdown
  - Source breakdown
  - Tag breakdown

Usage:
  python scripts/generate_readme.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Make sibling modules importable regardless of CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from formatters import code_bar, dash_if_empty, pluralize  # noqa: E402
from scanner import Problem, scan_problems  # noqa: E402
from stats import compute_stats  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"

START_MARKER = "<!-- DSA:AUTO:START -->"
END_MARKER = "<!-- DSA:AUTO:END -->"

RECENT_ACTIVITY_LIMIT = 10
RECENT_SOLVE_LIMIT = 10


# ---------------------------------------------------------------------------
# Section generators
# ---------------------------------------------------------------------------

def _link(problem: Problem) -> str:
    """Markdown link to the problem's README if it exists, else the folder."""
    readme = ROOT / problem.path / "README.md"
    label = problem.title or problem.slug
    if readme.exists():
        return f"[{label}]({problem.path}/README.md)"
    return f"[{label}]({problem.path})"


def generate_overview(stats: dict, problems: list[Problem]) -> str:
    """Overview section with progress bars for solve rate and difficulty."""
    s = stats["summary"]
    total = s["total"]
    solved = s["solved"]

    lines = [
        "## 📊 Overview",
        "",
        f"**Solve rate:** {code_bar(solved, total, width=30, show_count=True)}",
        "",
        "### Difficulty breakdown",
        "",
    ]

    diff = stats["by_difficulty"]
    for d, count in diff.items():
        lines.append(
            f"- **{d.title()}**: {code_bar(count, total, width=20, show_count=True)}"
        )

    lines.append("")
    lines.append("### Status breakdown")
    lines.append("")
    status = stats["by_status"]
    for st, count in status.items():
        if count > 0:
            lines.append(
                f"- **{st.replace('-', ' ').title()}**: "
                f"{code_bar(count, total, width=20, show_count=True)}"
            )

    return "\n".join(lines)


def generate_streak(stats: dict) -> str:
    """Streak and activity summary from git commit history."""
    st = stats["streak"]
    lines = [
        "## 🔥 Streak & Activity",
        "",
        f"- **Current streak:** {pluralize(st['current_streak'], 'day')}",
        f"- **Longest streak:** {pluralize(st['longest_streak'], 'day')}",
        f"- **Total active days:** {st['total_active_days']}",
        f"- **Last active:** {dash_if_empty(st.get('last_active', ''))}",
    ]
    return "\n".join(lines)


def generate_topic_sections(problems: list[Problem], stats: dict) -> str:
    """Topic-wise progress with per-topic solve bars and problem tables."""
    if not problems:
        return "## 🗂️ Topics\n\n_No problems tracked yet._"

    by_topic: dict[str, list[Problem]] = {}
    for p in problems:
        by_topic.setdefault(p.topic, []).append(p)

    topic_stats = stats["by_topic"]

    lines = ["## 🗂️ Topics"]
    for topic in sorted(by_topic):
        items = by_topic[topic]
        ts = topic_stats.get(topic, {"total": len(items), "solved": 0})
        t_total = ts["total"]
        t_solved = ts["solved"]

        lines.append("")
        lines.append(f"### {topic} ({t_solved}/{t_total} solved)")
        lines.append("")
        lines.append(code_bar(t_solved, t_total, width=25, show_percent=True, show_count=True))
        lines.append("")
        lines.append("| Problem | Difficulty | Status | Time | Space | Source |")
        lines.append("|---------|-----------|--------|------|-------|--------|")
        for p in sorted(items, key=lambda x: x.title.lower()):
            lines.append(
                f"| {_link(p)} | {dash_if_empty(p.difficulty)} | "
                f"{dash_if_empty(p.status)} | {dash_if_empty(p.time_complexity)} | "
                f"{dash_if_empty(p.space_complexity)} | {dash_if_empty(p.platform)} |"
            )
    return "\n".join(lines)


def generate_solved_table(problems: list[Problem]) -> str:
    """Full solved problems table sorted by solved date."""
    solved = [p for p in problems if p.is_solved]
    if not solved:
        return "## ✅ Solved Problems\n\n_No problems solved yet._"

    solved.sort(key=lambda p: (p.solved_date, p.title))

    lines = [
        "## ✅ Solved Problems",
        "",
        f"_{len(solved)} problem(s) solved_",
        "",
        "| # | Problem | Topic | Difficulty | Time | Space | Source | Solved |",
        "|---|---------|-------|-----------|------|-------|--------|--------|",
    ]
    for i, p in enumerate(solved, 1):
        lines.append(
            f"| {i} | {_link(p)} | {p.topic} | {dash_if_empty(p.difficulty)} | "
            f"{dash_if_empty(p.time_complexity)} | {dash_if_empty(p.space_complexity)} | "
            f"{dash_if_empty(p.platform)} | {dash_if_empty(p.solved_date)} |"
        )
    return "\n".join(lines)


def generate_recent_solves(stats: dict) -> str:
    """Recent solves section from the stats payload."""
    solves = stats["recent_solves"][:RECENT_SOLVE_LIMIT]
    if not solves:
        return "## 🏆 Recent Solves\n\n_No solves recorded yet._"

    lines = [
        "## 🏆 Recent Solves",
        "",
        "| Date | Problem | Topic | Difficulty | Source |",
        "|------|---------|-------|-----------|--------|",
    ]
    for s in solves:
        lines.append(
            f"| {s['solved_date']} | {s['title']} | {s['topic']} | "
            f"{dash_if_empty(s['difficulty'])} | {dash_if_empty(s['source'])} |"
        )
    return "\n".join(lines)


def generate_recent_activity(stats: dict) -> str:
    """Recent activity section from the stats payload."""
    activity = stats["activity_timeline"][:RECENT_ACTIVITY_LIMIT]
    if not activity:
        return "## 🕐 Recent Activity\n\n_No attempts recorded yet._"

    lines = [
        "## 🕐 Recent Activity",
        "",
        "| Date | Problem | Topic | Outcome |",
        "|------|---------|-------|---------|",
    ]
    for a in activity:
        lines.append(
            f"| {a['date']} | {a['problem']} | {a['topic']} | {a['outcome']} |"
        )
    return "\n".join(lines)


def generate_language_breakdown(stats: dict) -> str:
    """Language breakdown with bars."""
    langs = stats["by_language"]
    if not langs:
        return "## 💻 Language Breakdown\n\n_No problems tracked yet._"

    total = sum(langs.values())
    lines = [
        "## 💻 Language Breakdown",
        "",
    ]
    for lang, count in langs.items():
        lines.append(
            f"- **{lang}**: {code_bar(count, total, width=20, show_count=True)}"
        )
    return "\n".join(lines)


def generate_source_breakdown(stats: dict) -> str:
    """Source/platform breakdown with bars."""
    sources = stats["by_source"]
    if not sources:
        return "## 🌐 Source Breakdown\n\n_No sources tracked yet._"

    total = sum(sources.values())
    lines = [
        "## 🌐 Source Breakdown",
        "",
    ]
    for source, count in sources.items():
        lines.append(
            f"- **{source}**: {code_bar(count, total, width=20, show_count=True)}"
        )
    return "\n".join(lines)


def generate_tag_breakdown(stats: dict) -> str:
    """Tag breakdown (only shown if tags exist)."""
    tags = stats["by_tag"]
    if not tags:
        return ""

    total = sum(tags.values())
    lines = [
        "## 🏷️ Tag Breakdown",
        "",
    ]
    for tag, count in tags.items():
        lines.append(
            f"- **{tag}**: {code_bar(count, total, width=15, show_count=True)}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# README assembly
# ---------------------------------------------------------------------------

def generate_content(stats: dict, problems: list[Problem]) -> str:
    """Assemble the full auto-generated block (including markers)."""
    sections = [
        START_MARKER,
        "<!-- Auto-generated by scripts/generate_readme.py — do not edit between markers. -->",
        generate_overview(stats, problems),
        generate_streak(stats),
        generate_topic_sections(problems, stats),
        generate_solved_table(problems),
        generate_recent_solves(stats),
        generate_recent_activity(stats),
        generate_language_breakdown(stats),
        generate_source_breakdown(stats),
        generate_tag_breakdown(stats),
        END_MARKER,
    ]
    # Filter out empty sections (e.g. tag breakdown when no tags)
    sections = [s for s in sections if s]
    return "\n\n".join(sections)


def update_readme(stats: dict, problems: list[Problem]) -> bool:
    """Replace content between markers in README.md. Returns True if changed."""
    content = generate_content(stats, problems)

    if README_PATH.exists():
        text = README_PATH.read_text(encoding="utf-8")
        if START_MARKER in text and END_MARKER in text:
            pattern = re.compile(
                re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
                re.DOTALL,
            )
            new_text = pattern.sub(content, text)
        else:
            anchor = "## 🚀 Quick start"
            if anchor in text:
                new_text = text.replace(anchor, content + "\n\n---\n\n" + anchor, 1)
            else:
                new_text = text.rstrip() + "\n\n" + content + "\n"
    else:
        new_text = content + "\n"

    old_text = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    if new_text == old_text:
        return False

    README_PATH.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    stats = compute_stats()
    problems = scan_problems()
    changed = update_readme(stats, problems)
    print(f"Scanned {len(problems)} problem(s).")
    if changed:
        print(f"Updated {README_PATH.relative_to(ROOT)}")
    else:
        print(f"No changes needed — {README_PATH.relative_to(ROOT)} is up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())