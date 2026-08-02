#!/usr/bin/env python3
"""
Compute analytics statistics from scanned problem metadata and git history.

This module is the single source of truth for all dashboard numbers.
It is consumed by:
  - scripts/generate_dashboard.py  (writes dashboard/stats.json)
  - scripts/generate_readme.py     (renders stats into README sections)

Usage:
  from stats import compute_stats
  data = compute_stats()
"""

from __future__ import annotations

import subprocess
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

# Make sibling scanner.py importable regardless of CWD.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scanner import Problem, scan_problems  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "problems"

DIFFICULTY_ORDER = ["easy", "medium", "hard"]
STATUS_ORDER = ["solved", "reviewed", "in-progress", "todo"]
RECENT_SOLVE_LIMIT = 10


def _safe_date(s: str) -> date | None:
    """Parse an ISO date string safely."""
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _git_commit_dates() -> list[date]:
    """Return dates of commits that touched problems/ (best-effort)."""
    if not PROBLEMS_DIR.exists():
        return []
    try:
        result = subprocess.run(
            ["git", "log", "--format=%cI", "--", "problems/"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    dates: list[date] = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            dates.append(datetime.fromisoformat(line).date())
        except ValueError:
            continue
    return dates


def _compute_streak(commit_dates: list[date]) -> dict[str, Any]:
    """Compute current streak, longest streak, and total active days."""
    if not commit_dates:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_active_days": 0,
            "last_active": None,
        }

    unique_days = sorted(set(commit_dates), reverse=True)
    today = date.today()

    # Current streak: consecutive days ending today or yesterday
    current = 0
    check = today
    if unique_days[0] < check:
        # If last commit was yesterday, streak still counts
        if unique_days[0] == check - timedelta(days=1):
            check = unique_days[0]
        else:
            current = 0
            check = None

    if check is not None:
        for d in unique_days:
            if d == check:
                current += 1
                check -= timedelta(days=1)
            elif d < check:
                break

    # Longest streak
    longest = 0
    run = 0
    prev: date | None = None
    for d in sorted(unique_days):
        if prev is not None and d == prev + timedelta(days=1):
            run += 1
        else:
            run = 1
        longest = max(longest, run)
        prev = d

    return {
        "current_streak": current,
        "longest_streak": longest,
        "total_active_days": len(unique_days),
        "last_active": unique_days[0].isoformat(),
    }


def _recent_solves(problems: list[Problem]) -> list[dict[str, Any]]:
    """Return the most recently solved problems, newest first."""
    solved = [p for p in problems if p.is_solved and p.solved_date]
    solved.sort(key=lambda p: p.solved_date, reverse=True)
    return [
        {
            "title": p.title or p.slug,
            "topic": p.topic,
            "difficulty": p.difficulty,
            "source": p.platform,
            "solved_date": p.solved_date,
            "path": p.path,
        }
        for p in solved[:RECENT_SOLVE_LIMIT]
    ]


def _activity_timeline(problems: list[Problem]) -> list[dict[str, Any]]:
    """Collect all attempts across problems, sorted by date descending."""
    rows: list[dict[str, Any]] = []
    for p in problems:
        for att in p.attempts:
            d = att.get("date", "")
            outcome = att.get("outcome", "")
            if d and outcome:
                rows.append({
                    "date": d,
                    "problem": p.title or p.slug,
                    "topic": p.topic,
                    "outcome": outcome,
                })
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


def compute_stats() -> dict[str, Any]:
    """Compute the full statistics payload from the repository."""
    problems = scan_problems()

    total = len(problems)
    solved = sum(1 for p in problems if p.is_solved)
    in_progress = sum(1 for p in problems if p.status == "in-progress")
    todo = sum(1 for p in problems if p.status == "todo")

    # By difficulty
    diff_counts = Counter(p.difficulty for p in problems if p.difficulty)
    by_difficulty = {
        d: diff_counts.get(d, 0) for d in DIFFICULTY_ORDER
    }

    # By status
    status_counts = Counter(p.status for p in problems if p.status)
    by_status = {s: status_counts.get(s, 0) for s in STATUS_ORDER}

    # By topic
    topic_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "solved": 0}
    )
    for p in problems:
        topic_counts[p.topic]["total"] += 1
        if p.is_solved:
            topic_counts[p.topic]["solved"] += 1
    by_topic = {
        t: dict(v) for t, v in sorted(topic_counts.items())
    }

    # By source/platform
    source_counts = Counter(p.platform for p in problems if p.platform)
    by_source = dict(sorted(source_counts.items(), key=lambda x: (-x[1], x[0])))

    # By language
    lang_counts = Counter(p.language for p in problems if p.language)
    by_language = dict(sorted(lang_counts.items(), key=lambda x: (-x[1], x[0])))

    # By tag
    tag_counts: Counter = Counter()
    for p in problems:
        for tag in p.tags:
            tag_counts[tag] += 1
    by_tag = dict(sorted(tag_counts.items(), key=lambda x: (-x[1], x[0])))

    # Streak from git history
    commit_dates = _git_commit_dates()
    streak = _compute_streak(commit_dates)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "total": total,
            "solved": solved,
            "in_progress": in_progress,
            "todo": todo,
            "solve_rate": round(solved / total, 4) if total else 0.0,
        },
        "by_difficulty": by_difficulty,
        "by_status": by_status,
        "by_topic": by_topic,
        "by_source": by_source,
        "by_language": by_language,
        "by_tag": by_tag,
        "streak": streak,
        "recent_solves": _recent_solves(problems),
        "activity_timeline": _activity_timeline(problems),
        # Full problem records for search/filter in the static site.
        "problems": [p.to_dict() for p in problems],
    }


def main() -> int:
    """Print the stats as JSON (for debugging / CLI use)."""
    import json
    print(json.dumps(compute_stats(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())