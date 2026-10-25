"""Count non-blank, non-comment Python lines in the agent (PRD L-03)."""

import sys
from pathlib import Path


def count(root="saysno"):
    lines = (l.strip() for f in sorted(Path(root).glob("*.py")) for l in f.read_text().splitlines())
    return sum(1 for l in lines if l and not l.startswith("#"))


if __name__ == "__main__":
    print(count(*sys.argv[1:]))
