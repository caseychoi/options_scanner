"""Claude Code status line for stockpile."""
import json
import os
import subprocess
import sys
from pathlib import Path

COLOR = "\033[38;2;6;182;212m"  # cyan-500
RESET = "\033[0m"
DIM = "\033[38;2;220;220;220m"  # light gray — readable on dark terminals
BOLD = "\033[1m"
LABEL = "stockpile"


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    cwd = data.get("cwd") or os.getcwd()
    model = (data.get("model") or {}).get("display_name") or "?"
    project_dir = (data.get("workspace") or {}).get("project_dir") or cwd
    output_style = (data.get("output_style") or {}).get("name") or "default"
    ctx_pct = (data.get("context_window") or {}).get("used_percentage")
    rate_limits = data.get("rate_limits") or {}
    five_hr_pct = (rate_limits.get("five_hour") or {}).get("used_percentage")
    seven_d_pct = (rate_limits.get("seven_day") or {}).get("used_percentage")
    thinking_on = (data.get("thinking") or {}).get("enabled", False)
    effort_level = (data.get("effort") or {}).get("level")

    try:
        rel = Path(cwd).relative_to(project_dir).as_posix()
        if rel in ("", "."):
            rel = None
    except (ValueError, TypeError):
        rel = cwd

    branch = "?"
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, stderr=subprocess.DEVNULL, text=True, timeout=2,
        )
        branch = out.strip() or "?"
    except Exception:
        pass

    model_str = model
    if thinking_on:
        model_str += " [think]"
    if effort_level:
        model_str += f" [{effort_level}]"

    parts = [
        f"{BOLD}{COLOR}[{LABEL}]{RESET}",
        f"{DIM}({branch}){RESET}",
        f"{DIM}{model_str}{RESET}",
    ]
    if rel:
        parts.append(f"{DIM}{rel}{RESET}")
    if output_style and output_style != "default":
        parts.append(f"{DIM}<{output_style}>{RESET}")
    if ctx_pct is not None:
        parts.append(f"{DIM}ctx {ctx_pct:.0f}%{RESET}")
    if five_hr_pct is not None:
        parts.append(f"{DIM}5h {five_hr_pct:.0f}%{RESET}")
    if seven_d_pct is not None:
        parts.append(f"{DIM}wk {seven_d_pct:.0f}%{RESET}")

    sys.stdout.write(" | ".join(parts))


if __name__ == "__main__":
    main()
