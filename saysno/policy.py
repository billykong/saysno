"""Which tool calls run. File tools are confined to the project by Tools.path;
bash commands need an allow-list match or the user's yes."""

import re

ALLOW = ["ls", "cat", "head", "tail", "wc", "grep", "find", "pwd", "pytest", "python -m pytest",
         "git status", "git diff", "git log", "git show"]
# Anything that chains, redirects or substitutes can hide a second command.
SHELL_META = re.compile(r"[;&|`$<>\n]")
# Endings models add to trim their own output (F-02): stderr into stdout, then head or tail.
TRIM = re.compile(r"(\s+2>&1)?(\s*\|\s*(head|tail)(\s+-n\s*\d+|\s+-\d+)?)?\s*$")


def decide(name, args, trim=False):
    """Return "allow" or "ask"."""
    return check(name, args, trim)[0]


def check(name, args, trim=False):
    """Return ("allow", None) or ("ask", why). With trim, a TRIM ending doesn't count."""
    if name != "bash":
        return "allow", None
    command = args.get("command", "").strip()
    if trim:
        command = command[:TRIM.search(command).start()]
    if meta := SHELL_META.search(command):
        return "ask", f"it contains {meta.group()!r}, which can chain, redirect or substitute commands"
    if any(command == p or command.startswith(p + " ") for p in ALLOW):
        return "allow", None
    return "ask", f"{command.split()[0] if command else 'an empty command'!r} is not on the allow list"


def ask_user(name, args):
    answer = input(f"  run `{args.get('command')}`? [y/N] ")
    return answer.strip().lower() == "y"
