#!/usr/bin/env python3
"""
Validate the DSA practice tracker repository.

Checks:
  1. Required template files exist.
  2. Every problem folder lives at problems/<topic>/<problem-name>/.
  3. Every problem folder contains metadata.json and Solution.java.
  4. metadata.json is valid JSON with all required fields and allowed values.
  5. Folder names follow kebab-case.
  6. topic in metadata matches the topic folder name.
  7. Dates are valid ISO (YYYY-MM-DD) and updatedAt >= createdAt.
  8. No misplaced metadata.json / Solution.java files.
  9. No duplicate problem slugs across topics (warning).
  10. No duplicate problems (same platform + problemId).

Usage:
  python scripts/validate.py
Exit code:
  0 = all good, non-zero = errors found.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = ROOT / "problems"
TEMPLATES_DIR = ROOT / "templates"

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_FIELDS = [
    "title", "topic", "source", "difficulty",
    "status", "language", "createdAt", "updatedAt",
]
ALLOWED_DIFFICULTY = {"easy", "medium", "hard"}
ALLOWED_STATUS = {"todo", "in-progress", "solved", "reviewed"}
ALLOWED_OUTCOMES = {"accepted", "wrong-answer", "timeout", "gave-up", "reviewed"}
EXPECTED_TEMPLATES = ["Solution.java", "README.md", "notes.md", "metadata.json"]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.problems_checked = 0

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def summary(self) -> str:
        lines = [
            f"Problems checked: {self.problems_checked}",
            f"Warnings: {len(self.warnings)}",
            f"Errors:   {len(self.errors)}",
        ]
        if self.warnings:
            lines.append("\nWarnings:")
            for w in self.warnings:
                lines.append(f"  WARN  {w}")
        if self.errors:
            lines.append("\nErrors:")
            for e in self.errors:
                lines.append(f"  FAIL  {e}")
        return "\n".join(lines)


def is_kebab(name: str) -> bool:
    return bool(KEBAB_RE.match(name))


def parse_iso(value: str) -> date | None:
    if not isinstance(value, str) or not ISO_DATE_RE.match(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def find_problem_folders() -> list[Path]:
    """Return all expected problem folders: problems/<topic>/<problem-name>."""
    folders: list[Path] = []
    if not PROBLEMS_DIR.exists():
        return folders
    for topic_dir in sorted(PROBLEMS_DIR.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("."):
            continue
        for problem_dir in sorted(topic_dir.iterdir()):
            if not problem_dir.is_dir() or problem_dir.name.startswith("."):
                continue
            folders.append(problem_dir)
    return folders


def validate_templates(report: Report) -> None:
    for name in EXPECTED_TEMPLATES:
        if not (TEMPLATES_DIR / name).exists():
            report.error(f"Missing template: templates/{name}")


def validate_stray_files(report: Report) -> None:
    """Flag metadata.json / Solution.java not at the correct depth."""
    if not PROBLEMS_DIR.exists():
        return
    for path in PROBLEMS_DIR.rglob("*"):
        if not path.is_file():
            continue
        if path.name in ("metadata.json", "Solution.java"):
            parts = path.relative_to(PROBLEMS_DIR).parts
            # Expected: <topic>/<problem-name>/<file>  => 3 parts
            if len(parts) != 3:
                report.error(
                    f"Misplaced file '{path.relative_to(ROOT)}' — must live at "
                    f"problems/<topic>/<problem-name>/{path.name}"
                )


def validate_metadata(problem_dir: Path, report: Report) -> None:
    rel = problem_dir.relative_to(ROOT)
    topic_name = problem_dir.parent.name
    meta_path = problem_dir / "metadata.json"

    if not meta_path.exists():
        report.error(f"{rel}: missing metadata.json")
        return

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.error(f"{rel}: metadata.json is not valid JSON ({exc})")
        return
    except OSError as exc:
        report.error(f"{rel}: cannot read metadata.json ({exc})")
        return

    if not isinstance(meta, dict):
        report.error(f"{rel}: metadata.json must be a JSON object")
        return

    # Required fields present and non-empty (for strings)
    for field in REQUIRED_FIELDS:
        if field not in meta:
            report.error(f"{rel}: metadata.json missing required field '{field}'")
            continue
        val = meta[field]
        if isinstance(val, str) and val.strip() == "":
            report.error(f"{rel}: metadata.json field '{field}' is empty")

    # source object
    source = meta.get("source")
    if "source" in meta:
        if not isinstance(source, dict):
            report.error(f"{rel}: metadata.json 'source' must be an object")
        else:
            platform = source.get("platform")
            if not isinstance(platform, str) or platform.strip() == "":
                report.error(f"{rel}: metadata.json source.platform is missing or empty")

    # difficulty
    difficulty = meta.get("difficulty")
    if isinstance(difficulty, str) and difficulty not in ALLOWED_DIFFICULTY:
        report.error(
            f"{rel}: invalid difficulty '{difficulty}' "
            f"(allowed: {sorted(ALLOWED_DIFFICULTY)})"
        )

    # status
    status = meta.get("status")
    if isinstance(status, str) and status not in ALLOWED_STATUS:
        report.error(
            f"{rel}: invalid status '{status}' "
            f"(allowed: {sorted(ALLOWED_STATUS)})"
        )

    # topic matches folder
    topic_meta = meta.get("topic")
    if isinstance(topic_meta, str) and topic_meta != topic_name:
        report.error(
            f"{rel}: metadata.json topic '{topic_meta}' "
            f"does not match folder '{topic_name}'"
        )

    # dates
    created = meta.get("createdAt")
    updated = meta.get("updatedAt")
    created_date = parse_iso(created) if isinstance(created, str) else None
    updated_date = parse_iso(updated) if isinstance(updated, str) else None
    if isinstance(created, str) and created_date is None:
        report.error(f"{rel}: invalid createdAt '{created}' (expected YYYY-MM-DD)")
    if isinstance(updated, str) and updated_date is None:
        report.error(f"{rel}: invalid updatedAt '{updated}' (expected YYYY-MM-DD)")
    if created_date and updated_date and updated_date < created_date:
        report.error(f"{rel}: updatedAt ({updated}) is before createdAt ({created})")

    # attempts
    attempts = meta.get("attempts")
    if attempts is not None:
        if not isinstance(attempts, list):
            report.error(f"{rel}: metadata.json 'attempts' must be a list")
        else:
            for i, att in enumerate(attempts):
                if not isinstance(att, dict):
                    report.error(f"{rel}: attempts[{i}] must be an object")
                    continue
                att_date = att.get("date")
                if not isinstance(att_date, str) or parse_iso(att_date) is None:
                    report.error(f"{rel}: attempts[{i}].date invalid or missing")
                att_outcome = att.get("outcome")
                if not isinstance(att_outcome, str) or att_outcome not in ALLOWED_OUTCOMES:
                    report.error(
                        f"{rel}: attempts[{i}].outcome invalid '{att_outcome}' "
                        f"(allowed: {sorted(ALLOWED_OUTCOMES)})"
                    )


def validate_solution_class(problem_dir: Path, report: Report) -> None:
    rel = problem_dir.relative_to(ROOT)
    sol_path = problem_dir / "Solution.java"
    if not sol_path.exists():
        return
    class_name = "".join(p.capitalize() for p in problem_dir.name.split("-"))
    try:
        sol_text = sol_path.read_text(encoding="utf-8")
    except OSError:
        return
    if not re.search(r"\bclass\s+" + re.escape(class_name) + r"\b", sol_text):
        report.warn(
            f"{rel}: Solution.java class name should be '{class_name}' "
            f"(derived from '{problem_dir.name}')"
        )


def validate_problem_folder(problem_dir: Path, report: Report) -> None:
    report.problems_checked += 1
    rel = problem_dir.relative_to(ROOT)
    topic_name = problem_dir.parent.name
    problem_name = problem_dir.name

    # Naming conventions
    if not is_kebab(topic_name):
        report.error(f"{rel}: topic folder '{topic_name}' is not kebab-case")
    if not is_kebab(problem_name):
        report.error(f"{rel}: problem folder '{problem_name}' is not kebab-case")

    # Required files
    if not (problem_dir / "metadata.json").exists():
        report.error(f"{rel}: missing metadata.json")
    if not (problem_dir / "Solution.java").exists():
        report.error(f"{rel}: missing Solution.java")

    validate_metadata(problem_dir, report)
    validate_solution_class(problem_dir, report)


def validate_duplicate_slugs(report: Report) -> None:
    """Warn about duplicate problem slugs across topics."""
    slug_topics: dict[str, list[str]] = {}
    for problem_dir in find_problem_folders():
        slug = problem_dir.name
        topic = problem_dir.parent.name
        slug_topics.setdefault(slug, []).append(topic)
    for slug, topics in slug_topics.items():
        if len(topics) > 1:
            report.warn(
                f"Duplicate slug '{slug}' found in topics: "
                f"{', '.join(sorted(topics))}"
            )


def validate_duplicate_sources(report: Report) -> None:
    """Error on duplicate problems (same platform + problemId)."""
    seen: dict[str, str] = {}
    for problem_dir in find_problem_folders():
        meta_path = problem_dir / "metadata.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        source = meta.get("source")
        if not isinstance(source, dict):
            continue
        platform = str(source.get("platform", ""))
        problem_id = str(source.get("problemId", ""))
        if not platform or not problem_id:
            continue
        key = f"{platform}::{problem_id}"
        rel = str(problem_dir.relative_to(ROOT)).replace("\\", "/")
        if key in seen:
            report.error(
                f"Duplicate problem: '{rel}' and '{seen[key]}' "
                f"share source {platform} #{problem_id}"
            )
        else:
            seen[key] = rel


def main() -> int:
    report = Report()
    validate_templates(report)
    validate_stray_files(report)
    for problem_dir in find_problem_folders():
        validate_problem_folder(problem_dir, report)
    validate_duplicate_slugs(report)
    validate_duplicate_sources(report)

    print(report.summary())
    if report.errors:
        print("\nValidation FAILED. Fix the errors above before committing.")
        return 1
    print("\nValidation PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())