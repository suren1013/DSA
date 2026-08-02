"""Shared configuration and constants for the CLI."""

from __future__ import annotations

from pathlib import Path

# Repository root (parent of the cli/ package directory).
REPO_ROOT = Path(__file__).resolve().parent.parent

# Core directories.
PROBLEMS_DIR = REPO_ROOT / "problems"
SCRIPTS_DIR = REPO_ROOT / "scripts"
TEMPLATES_DIR = REPO_ROOT / "templates"
DASHBOARD_DIR = REPO_ROOT / "dashboard"
SITE_DIR = REPO_ROOT / "site"

# Metadata field values used by the CLI.
STATUS_SOLVING = "Solving"
STATUS_SOLVED = "Solved"
DIFFICULTY_UNKNOWN = "Unknown"
DEFAULT_LANGUAGE = "Java"
DEFAULT_SOURCE = "custom"

# Validation / generation commands.
VALIDATE_CMD = [SCRIPTS_DIR / "validate.py"]

# Filenames created inside a problem folder.
SOLUTION_FILENAME = "Solution.java"
METADATA_FILENAME = "metadata.json"
NOTES_FILENAME = "notes.md"

# Metadata schema version.
METADATA_VERSION = 1