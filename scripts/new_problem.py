#!/usr/bin/env python3
"""
Scaffold a new DSA problem folder.

Creates problems/<topic>/<problem-name>/ with Solution.java, metadata.json,
README.md, and notes.md pre-filled from templates/.

Examples:
  python scripts/new_problem.py --topic arrays --name two-sum \\
      --title "Two Sum" --difficulty easy --source LeetCode \\
      --url https://leetcode.com/problems/two-sum/ --source-id 1
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "problems"
TEMPLATES_DIR = ROOT / "templates"
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def is_kebab(name: str) -> bool:
    return bool(KEBAB_RE.match(name))


def class_name_from_slug(slug: str) -> str:
    """Convert a kebab-case slug to PascalCase: 'two-sum' -> 'TwoSum'."""
    return "".join(part.capitalize() for part in slug.split("-"))


def build_metadata(args: argparse.Namespace, today: str) -> dict:
    return {
        "title": args.title,
        "topic": args.topic,
        "source": {
            "platform": args.source,
            "url": args.url or "",
            "problemId": args.source_id or "",
        },
        "difficulty": args.difficulty,
        "status": args.status,
        "language": "java",
        "tags": [],
        "timeComplexity": "",
        "spaceComplexity": "",
        "attempts": [],
        "createdAt": today,
        "updatedAt": today,
    }


def fill_template(template_name: str, mapping: dict) -> str:
    text = (TEMPLATES_DIR / template_name).read_text(encoding="utf-8")
    for key, val in mapping.items():
        text = text.replace("{{" + key + "}}", val)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new DSA problem folder."
    )
    parser.add_argument("--topic", required=True, help="Topic slug (kebab-case)")
    parser.add_argument("--name", required=True, help="Problem slug (kebab-case)")
    parser.add_argument("--title", required=True, help="Human-readable title")
    parser.add_argument(
        "--difficulty", required=True,
        choices=["easy", "medium", "hard"],
    )
    parser.add_argument("--source", required=True, help="Platform/source name")
    parser.add_argument("--url", default="", help="Problem URL")
    parser.add_argument("--source-id", default="", help="Platform problem id")
    parser.add_argument(
        "--status", default="todo",
        choices=["todo", "in-progress", "solved", "reviewed"],
    )
    args = parser.parse_args()

    if not is_kebab(args.topic):
        print(f"FAIL  topic '{args.topic}' is not kebab-case")
        return 1
    if not is_kebab(args.name):
        print(f"FAIL  name '{args.name}' is not kebab-case")
        return 1

    problem_dir = PROBLEMS_DIR / args.topic / args.name
    if problem_dir.exists():
        print(f"FAIL  already exists: {problem_dir.relative_to(ROOT)}")
        return 1

    today = date.today().isoformat()
    class_name = class_name_from_slug(args.name)

    problem_dir.mkdir(parents=True)

    # Solution.java
    solution = fill_template("Solution.java", {
        "TITLE": args.title,
        "TOPIC": args.topic,
        "SOURCE": args.source,
        "URL": args.url or "N/A",
        "DESCRIPTION": "TODO: describe the problem.",
        "APPROACH": "TODO: describe the approach.",
        "TIME_COMPLEXITY": "TODO",
        "SPACE_COMPLEXITY": "TODO",
        "CLASS_NAME": class_name,
    })
    (problem_dir / "Solution.java").write_text(solution, encoding="utf-8")

    # README.md
    readme = fill_template("README.md", {
        "TITLE": args.title,
        "TOPIC": args.topic,
        "DIFFICULTY": args.difficulty,
        "URL": args.url or "N/A",
        "TIME_COMPLEXITY": "TODO",
        "SPACE_COMPLEXITY": "TODO",
    })
    (problem_dir / "README.md").write_text(readme, encoding="utf-8")

    # notes.md
    notes = fill_template("notes.md", {"TITLE": args.title})
    (problem_dir / "notes.md").write_text(notes, encoding="utf-8")

    # metadata.json (built directly to guarantee valid JSON)
    metadata = build_metadata(args, today)
    (problem_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    print(f"OK    Created {problem_dir.relative_to(ROOT)}")
    print(f"      class: {class_name}")
    print("      Next: implement Solution.java, then run: python scripts/validate.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())