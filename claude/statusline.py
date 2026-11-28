#!/usr/bin/env python3
"""Claude Code status line: context window usage, model, effort level, and git branch.

Example: "📦 20.3k 🦀 Opus 5.5 🧠 Medium 🌳 main (3 files, +42/-7)"
"""
import json
import re
import subprocess
import sys


def fmt(n: int) -> str:
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return f"{n / 1_000_000:.1f}m".replace(".0m", "m")


def git(cwd: str | None, *args: str) -> str | None:
    """Run a git command and return its stdout, or None if it failed."""
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=cwd or None,
            capture_output=True,
            text=True,
            timeout=1,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def git_changes(cwd: str | None) -> tuple[int, int, int] | None:
    """Files changed, lines added and lines removed compared with HEAD."""
    stat = git(cwd, "diff", "--shortstat", "HEAD")
    if stat is None:
        return None

    def num(pattern: str) -> int:
        m = re.search(pattern, stat)
        return int(m.group(1)) if m else 0

    return num(r"(\d+) files? changed"), num(r"(\d+) insertions?"), num(r"(\d+) deletions?")


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        data = {}

    cw = data.get("context_window") or {}
    usage = cw.get("current_usage") or {}
    tokens = (
        (usage.get("input_tokens") or 0)
        + (usage.get("cache_creation_input_tokens") or 0)
        + (usage.get("cache_read_input_tokens") or 0)
    )
    model_name = (data.get("model") or {}).get("display_name") or ""
    if model_name.startswith("Claude "):
        model_name = model_name[len("Claude "):]

    effort_level = (data.get("effort") or {}).get("level") or ""

    cwd = (data.get("workspace") or {}).get("current_dir") or data.get("cwd")
    branch = git(cwd, "branch", "--show-current") or ""
    changes = git_changes(cwd) if branch else None

    # Mid-tone colors with roughly 4.5:1 contrast on both white and near-black
    # backgrounds, so they read well in light and dark themes alike.
    GREEN = "\033[38;2;24;138;64m"  # #188a40
    RED = "\033[38;2;208;54;79m"  # #d0364f
    RESET = "\033[0m"

    parts = [f"📦 {fmt(tokens)}"]
    if model_name:
        parts.append(f"🦀 {model_name}")
    if effort_level:
        parts.append(f"🧠 {effort_level.capitalize()}")
    if branch:
        branch_part = f"🌳 {branch}"
        if changes:
            files, added, removed = changes
            if files:
                label = "file" if files == 1 else "files"
                branch_part += (
                    f" ({files} {label}, "
                    f"{GREEN}+{added}{RESET}/{RED}-{removed}{RESET})"
                )
            else:
                branch_part += " (clean)"
        parts.append(branch_part)
    print(" ".join(parts))


if __name__ == "__main__":
    main()
