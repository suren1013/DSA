#!/usr/bin/env python3
"""
Generate the dashboard/stats.json file with computed statistics.

This is the machine-readable companion to the README dashboard sections.
Future tools (web dashboards, CLIs, exports) can read this JSON directly
without re-scanning the repository.

Usage:
  python scripts/generate_dashboard.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make sibling modules importable regardless of CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from stats import compute_stats  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = ROOT / "dashboard"
STATS_PATH = DASHBOARD_DIR / "stats.json"


def main() -> int:
    stats = compute_stats()

    DASHBOARD_DIR.mkdir(exist_ok=True)
    STATS_PATH.write_text(
        json.dumps(stats, indent=2) + "\n", encoding="utf-8"
    )

    s = stats["summary"]
    st = stats["streak"]
    print(f"Generated {STATS_PATH.relative_to(ROOT)}")
    print(f"  Total problems:  {s['total']}")
    print(f"  Solved:          {s['solved']}")
    print(f"  Solve rate:      {s['solve_rate']:.1%}")
    print(f"  Current streak:  {st['current_streak']} day(s)")
    print(f"  Longest streak:  {st['longest_streak']} day(s)")
    print(f"  Active days:     {st['total_active_days']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())