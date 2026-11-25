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

    BRIGHT_WHITE = "\033[97m"
    GREEN = "\033[38;2;56;166;96m"  # #38a660, Claude Code dark theme diffAddedWord
    RED = "\033[38;2;179;89;107m"  # #b3596b, Claude Code dark theme diffRemovedWord
    RESET = "\033[0m"

    parts = [f"📦 {BRIGHT_WHITE}{fmt(tokens)}{RESET}"]
    if model_name:
        parts.append(f"🦀 {BRIGHT_WHITE}{model_name}{RESET}")
    if effort_level:
        parts.append(f"🧠 {BRIGHT_WHITE}{effort_level.capitalize()}{RESET}")
    if branch:
        branch_part = f"🌳 {BRIGHT_WHITE}{branch}{RESET}"
        if changes:
            files, added, removed = changes
            if files:
                label = "file" if files == 1 else "files"
                branch_part += (
                    f" {BRIGHT_WHITE}({files} {label}, "
                    f"{GREEN}+{added}{BRIGHT_WHITE}/{RED}-{removed}{BRIGHT_WHITE}){RESET}"
                )
            else:
                branch_part += f" {BRIGHT_WHITE}(clean){RESET}"
        parts.append(branch_part)
    print(" ".join(parts))


if __name__ == "__main__":
    main()
