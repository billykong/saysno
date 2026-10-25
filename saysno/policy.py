"""Which tool calls run. File tools are confined to the project by Tools.path;
bash commands need an allow-list match or the user's yes."""

import re

ALLOW = ["ls", "cat", "head", "tail", "wc", "grep", "find", "pwd", "pytest", "python -m pytest",
         "git status", "git diff", "git log", "git show"]
# Anything that chains, redirects or substitutes can hide a second command.
SHELL_META = re.compile(r"[;&|`$<>\n]")


def decide(name, args):
    """Return "allow" or "ask"."""
    if name != "bash":
        return "allow"
    command = args.get("command", "").strip()
    if SHELL_META.search(command):
        return "ask"
    if any(command == p or command.startswith(p + " ") for p in ALLOW):
        return "allow"
    return "ask"


def ask_user(name, args):
    answer = input(f"  run `{args.get('command')}`? [y/N] ")
    return answer.strip().lower() == "y"
