#!/usr/bin/env python3
"""PreToolUse guard for the qa-engineer agent.

Edit/Write/NotebookEdit: allowed only for files under <project>/tests/.
Bash: allowed only for an allow-list of read/test commands, no output redirection.
Exit code 2 blocks the tool call and shows stderr to Claude.
"""
import json
import os
import re
import shlex
import sys
from pathlib import Path

ALLOWED_BASH = (
    "pytest", "python -m pytest", "python3 -m pytest", ".venv/bin/python -m pytest",
    "python verify/run.py", "python3 verify/run.py", ".venv/bin/python verify/run.py",
    "ls", "cat", "head", "tail", "wc", "grep", "rg", "find", "pwd", "echo",
    "git status", "git diff", "git log", "git show",
)


def deny(msg: str) -> None:
    print(f"QA Engineer guard: {msg}", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
    tests = root / "tests"

    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        raw = inp.get("file_path") or inp.get("notebook_path") or ""
        target = Path(raw)
        if not target.is_absolute():
            target = root / target
        target = target.resolve()
        if target != tests and tests not in target.parents:
            deny(f"'{raw}' is outside tests/. QA Engineer may only edit tests/. "
                 "Report the production bug with a failing test instead of fixing it.")
        return

    if tool == "Bash":
        cmd = inp.get("command", "")
        cleaned = cmd.replace("2>&1", "")
        if re.search(r">|\btee\b|\$\(|`", cleaned):
            deny("output redirection / command substitution is not allowed.")
        for seg in re.split(r"&&|\|\||;|\|", cleaned):
            seg = seg.strip()
            if not seg:
                continue
            try:
                norm = " ".join(shlex.split(seg))
            except ValueError:
                deny(f"could not parse command segment: {seg!r}")
            if seg.startswith("cd "):
                continue
            words = norm.split()
            if words and words[0] == "find" and any(
                w in ("-delete", "-exec", "-execdir", "-ok", "-okdir") or w.startswith(("-fprint", "-fls"))
                for w in words
            ):
                deny("find with -delete/-exec/-ok/-fprint can modify files; not allowed.")
            if words and words[0] == "git" and any(w.startswith(("--output", "-o")) for w in words[2:]):
                deny("git --output writes files; not allowed.")
            if not any(norm == p or norm.startswith(p + " ") for p in ALLOWED_BASH):
                deny(f"command not in QA allow-list: {seg!r}. Allowed: pytest, verify, read-only shell/git.")
        return


if __name__ == "__main__":
    main()
