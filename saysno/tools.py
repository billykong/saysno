"""The four tools. Each returns text for the model or raises ToolError."""

import re
import subprocess
from pathlib import Path


class ToolError(Exception):
    """A failure the model should see and can correct."""


def _schema(description, **props):
    required = [k for k, v in props.items() if not v.pop("optional", False)]
    return {"description": description,
            "input_schema": {"type": "object", "properties": props, "required": required}}


SCHEMAS = {
    "read_file": _schema("Read a file's lines, numbered from 1.",
                         path={"type": "string"},
                         offset={"type": "integer", "description": "First line, default 1", "optional": True},
                         limit={"type": "integer", "description": "Number of lines, default 200", "optional": True}),
    "edit_file": _schema("Replace one exact occurrence of old with new. Fails if old is absent or not unique.",
                         path={"type": "string"}, old={"type": "string"}, new={"type": "string"}),
    "bash": _schema("Run a shell command in the project directory.", command={"type": "string"}),
    "grep": _schema("Search files for a regular expression; returns path:line:text.",
                    pattern={"type": "string"},
                    path={"type": "string", "description": "File or directory, default .", "optional": True}),
}
TOOLS = [{"name": name, **schema} for name, schema in SCHEMAS.items()]


class Tools:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def path(self, p):
        full = (self.root / p).resolve()
        if not full.is_relative_to(self.root):
            raise ToolError(f"{p} is outside the project directory")
        return full

    def read_file(self, path, offset=1, limit=200):
        lines = self.path(path).read_text().splitlines()
        start = max(offset, 1) - 1
        shown = [f"{i:6}\t{line}" for i, line in enumerate(lines[start:start + limit], start + 1)]
        rest = len(lines) - start - len(shown)
        return "\n".join(shown) + (f"\n({rest} more lines; read again with a higher offset)" if rest > 0 else "")

    def edit_file(self, path, old, new):
        full = self.path(path)
        text = full.read_text()
        count = text.count(old) if old else 0
        if count != 1:
            raise ToolError(f"old text found {count} times in {path}; it must match exactly once")
        full.write_text(text.replace(old, new))
        return f"edited {path}"

    def bash(self, command):
        r = subprocess.run(command, shell=True, cwd=self.root, capture_output=True, text=True, timeout=120)
        return f"exit code {r.returncode}\n{r.stdout}{r.stderr}"

    def grep(self, pattern, path="."):
        regex = re.compile(pattern)
        base = self.path(path)
        files = [base] if base.is_file() else sorted(f for f in base.rglob("*") if f.is_file())
        hits = []
        for f in files:
            if ".git" in f.parts or "__pycache__" in f.parts:
                continue
            try:
                lines = f.read_text().splitlines()
            except UnicodeDecodeError:
                continue
            hits += [f"{f.relative_to(self.root)}:{n}:{line}" for n, line in enumerate(lines, 1) if regex.search(line)]
        return "\n".join(hits) or "no matches"

    def run(self, name, args):
        if name not in SCHEMAS:
            raise ToolError(f"unknown tool {name}")
        try:
            return getattr(self, name)(**args)
        except (OSError, re.error, subprocess.TimeoutExpired, TypeError) as e:
            raise ToolError(str(e)) from e
