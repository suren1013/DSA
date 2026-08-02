#!/usr/bin/env python3
"""
Scan the DSA repository for all problems and their metadata.

Reads problems/<topic>/<problem-name>/ folders, parses metadata.json
(or Solution.java comment block as a fallback), and returns structured data
that the README generator and other tools can consume.

Usage:
  python scripts/scanner.py            # print a JSON summary
  python scripts/scanner.py --pretty   # pretty-print
  from scanner import scan_problems     # import as a module
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "problems"

# Matches " * Key: value" inside a JavaDoc block
COMMENT_KV_RE = re.compile(r"^\s*\*?\s*([A-Za-z][A-Za-z ]*?)\s*:\s*(.+?)\s*$")


@dataclass
class Problem:
    """Structured representation of a single problem folder."""

    slug: str
    title: str
    topic: str
    path: str
    platform: str = ""
    url: str = ""
    problem_id: str = ""
    difficulty: str = ""
    status: str = ""
    language: str = "java"
    tags: list[str] = field(default_factory=list)
    time_complexity: str = ""
    space_complexity: str = ""
    attempts: list[dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    metadata_source: str = ""  # "metadata.json" or "Solution.java"

    @property
    def solved_date(self) -> str:
        """Best-effort solved date: latest accepted attempt, else updated_at, else created_at."""
        accepted = [
            a["date"] for a in self.attempts
            if a.get("outcome") == "accepted" and a.get("date")
        ]
        if accepted:
            return max(accepted)
        if self.status in ("solved", "reviewed") and self.updated_at:
            return self.updated_at
        return self.created_at

    @property
    def is_solved(self) -> bool:
        return self.status in ("solved", "reviewed")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["solved_date"] = self.solved_date
        d["is_solved"] = self.is_solved
        return d


def _rel(path: Path) -> str:
    """Return a forward-slash relative path from the repo root."""
    return str(path.relative_to(ROOT)).replace("\\", "/")


def parse_solution_comment(solution_path: Path) -> dict:
    """Parse key: value pairs from the top JavaDoc comment block in Solution.java."""
    try:
        text = solution_path.read_text(encoding="utf-8")
    except OSError:
        return {}

    match = re.search(r"/\*\*(.*?)\*/", text, re.DOTALL)
    if not match:
        return {}

    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        m = COMMENT_KV_RE.match(line)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip()
            if val:
                result[key] = val
    return result


def _from_comment(problem_dir: Path) -> Problem | None:
    """Build a Problem from Solution.java comment metadata (fallback)."""
    sol_path = problem_dir / "Solution.java"
    if not sol_path.exists():
        return None

    raw = parse_solution_comment(sol_path)
    if not raw:
        return None

    def get(*keys: str) -> str:
        for k in keys:
            if k in raw:
                return raw[k]
        return ""

    return Problem(
        slug=problem_dir.name,
        title=get("problem", "title"),
        topic=problem_dir.parent.name,
        path=_rel(problem_dir),
        platform=get("source", "platform"),
        url=get("link", "url"),
        problem_id=get("problem id", "problemid", "id"),
        difficulty=get("difficulty").lower(),
        status=get("status").lower() or "todo",
        language="java",
        time_complexity=get("time", "time complexity", "timecomplexity"),
        space_complexity=get("space", "space complexity", "spacecomplexity"),
        metadata_source="Solution.java",
    )


def _from_metadata(problem_dir: Path) -> Problem | None:
    """Build a Problem from metadata.json (primary source)."""
    meta_path = problem_dir / "metadata.json"
    if not meta_path.exists():
        return None

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    if not isinstance(meta, dict):
        return None

    source = meta.get("source") or {}
    if not isinstance(source, dict):
        source = {}

    return Problem(
        slug=problem_dir.name,
        title=str(meta.get("title", "")),
        topic=str(meta.get("topic", "")) or problem_dir.parent.name,
        path=_rel(problem_dir),
        platform=str(source.get("platform", "")),
        url=str(source.get("url", "")),
        problem_id=str(source.get("problemId", "")),
        difficulty=str(meta.get("difficulty", "")),
        status=str(meta.get("status", "")),
        language=str(meta.get("language", "java")),
        tags=list(meta.get("tags", [])),
        time_complexity=str(meta.get("timeComplexity", "")),
        space_complexity=str(meta.get("spaceComplexity", "")),
        attempts=list(meta.get("attempts", [])),
        created_at=str(meta.get("createdAt", "")),
        updated_at=str(meta.get("updatedAt", "")),
        metadata_source="metadata.json",
    )


def parse_problem_folder(problem_dir: Path) -> Problem | None:
    """Parse a single problem folder, preferring metadata.json over Solution.java."""
    problem = _from_metadata(problem_dir)
    if problem is not None:
        return problem
    return _from_comment(problem_dir)


def scan_problems() -> list[Problem]:
    """Scan all problem folders under problems/ and return structured data."""
    problems: list[Problem] = []
    if not PROBLEMS_DIR.exists():
        return problems

    for topic_dir in sorted(PROBLEMS_DIR.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("."):
            continue
        for problem_dir in sorted(topic_dir.iterdir()):
            if not problem_dir.is_dir() or problem_dir.name.startswith("."):
                continue
            problem = parse_problem_folder(problem_dir)
            if problem is not None:
                problems.append(problem)

    return problems


def main() -> int:
    pretty = "--pretty" in sys.argv
    problems = scan_problems()
    data = [p.to_dict() for p in problems]
    if pretty:
        print(json.dumps(data, indent=2))
    else:
        print(json.dumps(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())