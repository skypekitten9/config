#!/usr/bin/env python3
"""Claude Code status line: context window usage, model, and effort level.

Example: "📦 20.3k 🦀 Opus 5.5 🧠 Medium"
"""
import json
import sys


def fmt(n: int) -> str:
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return f"{n / 1_000_000:.1f}m".replace(".0m", "m")


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

    BRIGHT_WHITE = "\033[97m"
    RESET = "\033[0m"

    parts = [f"📦 {BRIGHT_WHITE}{fmt(tokens)}{RESET}"]
    if model_name:
        parts.append(f"🦀 {BRIGHT_WHITE}{model_name}{RESET}")
    if effort_level:
        parts.append(f"🧠 {BRIGHT_WHITE}{effort_level.capitalize()}{RESET}")
    print(" ".join(parts))


if __name__ == "__main__":
    main()
