"""Utility helpers: terminal colors, command execution, slugs, VS Code."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# ANSI colors (no-op when terminal does not support them)
# ---------------------------------------------------------------------------

class Colors:
    """Minimal ANSI color helper with graceful fallback."""

    def __init__(self, enabled: bool) -> None:
        self._enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        if not self._enabled:
            return text
        return f"\033[{code}m{text}\033[0m"

    def green(self, text: str) -> str:
        return self._wrap("32", text)

    def red(self, text: str) -> str:
        return self._wrap("31", text)

    def yellow(self, text: str) -> str:
        return self._wrap("33", text)

    def cyan(self, text: str) -> str:
        return self._wrap("36", text)

    def bold(self, text: str) -> str:
        return self._wrap("1", text)


def supports_color() -> bool:
    """Return True when the terminal supports ANSI colors."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not sys.stdout.isatty():
        return False
    platform = sys.platform
    if platform == "win32":
        # Modern Windows terminals support ANSI; best-effort detection.
        return "WT_SESSION" in os.environ or "ANSICON" in os.environ
    return True


c = Colors(supports_color())


def info(message: str) -> None:
    print(c.cyan(message))


def success(message: str) -> None:
    print(c.green(message))


def warn(message: str) -> None:
    print(c.yellow(message))


def error(message: str) -> None:
    print(c.red(message), file=sys.stderr)


# ---------------------------------------------------------------------------
# Slugs and identifiers
# ---------------------------------------------------------------------------

def to_slug(text: str) -> str:
    """Convert arbitrary text to a URL-safe kebab-case slug.

    Examples:
        "Two Sum"          -> "two-sum"
        "Binary Palindrome" -> "binary-palindrome"
        "My College Problem" -> "my-college-problem"
    """
    text = text.strip().lower()
    # Replace any non-alphanumeric run with a single hyphen.
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def title_case_from_slug(slug: str) -> str:
    """Convert a slug back to a Title Case label (used in commit messages)."""
    return " ".join(word.capitalize() for word in slug.split("-"))


# ---------------------------------------------------------------------------
# Command execution
# ---------------------------------------------------------------------------

def run_command(
    command: list[str],
    cwd: Path,
    description: str,
) -> subprocess.CompletedProcess:
    """Run an external command and surface failures with a friendly message.

    Raises SystemExit(1) when the command fails.
    """
    info(f"  → {description}")
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        error(f"Command not found: {command[0]}")
        error("Expected user mistake — check that the tool is installed and on PATH.")
        raise SystemExit(1)

    if result.returncode != 0:
        # Show the underlying output to help debugging, but avoid raw tracebacks.
        error(f"Command failed: {' '.join(command)}")
        if result.stdout.strip():
            print(result.stdout.strip(), file=sys.stderr)
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(1)

    return result


# ---------------------------------------------------------------------------
# VS Code integration
# ---------------------------------------------------------------------------

def open_in_vscode(path: Path) -> bool:
    """Open a file/folder in VS Code using the `code` CLI if available.

    Returns True on success, False when the CLI is unavailable (prints a
    friendly message instead of failing).
    """
    code_cli = shutil.which("code")
    if code_cli is None:
        warn("VS Code CLI (`code`) not found on PATH — skipping auto-open.")
        warn(f"Open the file manually: {path}")
        return False

    try:
        subprocess.Popen([code_cli, str(path)])
    except OSError as exc:
        warn(f"Could not launch VS Code: {exc}")
        warn(f"Open the file manually: {path}")
        return False

    success(f"Opened in VS Code: {path}")
    return True


# ---------------------------------------------------------------------------
# Pre-push verification (shared by `sp` and `reset`)
# ---------------------------------------------------------------------------

def verify_generated_files(root: Path) -> None:
    """Verify the repository is in a pushable state.

    Runs validate.py to confirm the structure and metadata are valid, then
    checks that the generated files are committed (no uncommitted changes).
    The `sp`/`reset` pipelines regenerate the files BEFORE committing, so by
    the time this is called they are expected to be committed already.

    Raises SystemExit(1) on any failure.
    """
    info("  → Verifying repository is ready to push…")

    # Validation first.
    run_command(
        ["python", "scripts/validate.py"],
        root,
        "Validate structure & metadata",
    )

    # Check git sees no uncommitted changes to the generated files.
    status = subprocess.run(
        ["git", "status", "--porcelain", "README.md", "dashboard/stats.json", "site/data/stats.json"],
        cwd=str(root), capture_output=True, text=True,
    )
    if status.stdout.strip():
        error("Generated files have uncommitted changes — commit them before pushing.")
        print(status.stdout.strip(), file=sys.stderr)
        raise SystemExit(1)

    success("✔ Generated files are up to date")


# ---------------------------------------------------------------------------
# Git push helper (shared by `sp` and `reset`)
# ---------------------------------------------------------------------------

def git_push(root: Path) -> None:
    """Push to the remote, handling upstream and behind-remote scenarios.

    Workflow:
      1. If no upstream is set, configure it.
      2. Fetch origin to check if the local branch is behind.
      3. If behind, rebase onto the latest remote.
      4. Retry push.

    Only fails on actual merge/rebase conflicts.
    """
    # Pre-push verification: ensure validate passes and generated files are
    # current. Since the generation scripts are idempotent, this catches any
    # drift caused by manual edits before we push stale data.
    verify_generated_files(root)

    # Determine the current branch.
    branch_result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=str(root), capture_output=True, text=True,
    )
    branch = branch_result.stdout.strip()
    if not branch:
        error("Could not determine the current git branch.")
        raise SystemExit(1)

    # Step 1: Ensure upstream tracking is configured.
    upstream_check = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=str(root), capture_output=True, text=True,
    )
    if upstream_check.returncode != 0:
        info(f"  → Setting upstream to origin/{branch}…")
        run_command(
            ["git", "push", "--set-upstream", "origin", branch],
            root, f"Configure upstream origin/{branch}",
        )
        success("✔ Upstream configured")
        return

    # Step 2: Fetch to see if we're behind.
    info("  → Fetching remote…")
    fetch_result = subprocess.run(
        ["git", "fetch", "origin"],
        cwd=str(root), capture_output=True, text=True,
    )
    if fetch_result.returncode != 0:
        # Fetch failed (e.g. no network) — try a direct push.
        try:
            run_command(["git", "push"], root, "Push to remote")
            success("✔ Push successful")
            return
        except SystemExit:
            error("Push failed and could not fetch remote for rebase.")
            raise

    success("✔ Fetch complete")

    # Step 3: Check if local is behind remote.
    behind_check = subprocess.run(
        ["git", "rev-list", "--count", f"HEAD..origin/{branch}"],
        cwd=str(root), capture_output=True, text=True,
    )
    behind_count = int(behind_check.stdout.strip()) if behind_check.stdout.strip().isdigit() else 0

    if behind_count > 0:
        info(f"  → Local is {behind_count} commit(s) behind — rebasing…")
        rebase_result = subprocess.run(
            ["git", "pull", "--rebase", "origin", branch],
            cwd=str(root), capture_output=True, text=True,
        )
        if rebase_result.returncode != 0:
            error("Rebase failed — there may be merge conflicts.")
            if rebase_result.stdout.strip():
                print(rebase_result.stdout.strip(), file=sys.stderr)
            if rebase_result.stderr.strip():
                print(rebase_result.stderr.strip(), file=sys.stderr)
            error("Resolve conflicts manually, then run `git rebase --continue`.")
            raise SystemExit(1)
        success("✔ Rebased onto latest remote")
    else:
        info("  → Local is up to date with remote")

    # Step 4: Push.
    run_command(["git", "push"], root, "Push to remote")
    success("✔ Push successful")


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

def today_iso() -> str:
    """Today's date as YYYY-MM-DD."""
    from datetime import date

    return date.today().isoformat()
