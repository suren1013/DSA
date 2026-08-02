#!/usr/bin/env python3
"""
Build the static site data for GitHub Pages.

Copies the machine-readable stats from dashboard/stats.json into site/data/
so the static site (site/index.html) can be deployed with zero build steps.

Usage:
  python scripts/build_site.py
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

# Make sibling modules importable regardless of CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
STATS_SRC = ROOT / "dashboard" / "stats.json"
SITE_DIR = ROOT / "site"
DATA_DIR = SITE_DIR / "data"


def main() -> int:
    if not STATS_SRC.exists():
        print("FAIL  dashboard/stats.json not found. Run scripts/generate_dashboard.py first.", file=sys.stderr)
        return 1

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Copy full stats to site/data/stats.json
    dest = DATA_DIR / "stats.json"
    shutil.copyfile(STATS_SRC, dest)

    print(f"OK    Copied {STATS_SRC.relative_to(ROOT)} -> {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())