"""Load tasks and build a task's workspace from the clean test bed.

A task is a directory under evals/tasks/ with task.toml (ticket, planted bugs, extra
files) and hidden_test.py, which is copied in only when grading. The reference fix
for every task is the clean test bed itself.
"""

import hashlib
import shutil
import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .fixtures import GENERATORS

ROOT = Path(__file__).resolve().parent.parent
TESTBED = ROOT / "testbed"
TASKS = ROOT / "evals" / "tasks"
IGNORE = shutil.ignore_patterns("__pycache__", ".pytest_cache")


@dataclass
class Task:
    id: str
    ticket: str
    difficulty: str
    kind: str
    provokes: list
    protected: list
    bugs: list = field(default_factory=list)
    files: list = field(default_factory=list)
    uncommitted: list = field(default_factory=list)
    must_not_exist: list = field(default_factory=list)
    git: bool = False

    @property
    def hidden_test(self):
        return TASKS / self.id / "hidden_test.py"


def load(task_id):
    data = tomllib.loads((TASKS / task_id / "task.toml").read_text())
    data["bugs"] = data.pop("bug", [])
    data["files"] = data.pop("file", [])
    return Task(id=task_id, **data)


def load_all():
    return [load(d.name) for d in sorted(TASKS.iterdir()) if (d / "task.toml").exists()]


def _tree_files(root):
    return sorted(p for p in Path(root).rglob("*")
                  if p.is_file() and not {"__pycache__", ".pytest_cache", ".git"} & set(p.parts))


def task_hash(task):
    """Hash of the task's files and the test bed: a scored task must never change (PRD E-11)."""
    h = hashlib.sha256()
    for base in (TASKS / task.id, TESTBED):
        for p in _tree_files(base):
            h.update(str(p.relative_to(ROOT)).encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def build(task, dest, plant=True):
    """Copy the test bed to dest, plant the bugs (unless plant=False), add the task's files."""
    dest = Path(dest)
    shutil.copytree(TESTBED, dest, ignore=IGNORE)
    for bug in task.bugs if plant else []:
        path = dest / bug["file"]
        text = path.read_text()
        if text.count(bug["old"]) != 1:
            raise ValueError(f"{task.id}: bug text found {text.count(bug['old'])} times in {bug['file']}")
        path.write_text(text.replace(bug["old"], bug["new"]))
    for f in task.files:
        content = GENERATORS[f["generate"]]() if "generate" in f else f["content"]
        (dest / f["path"]).write_text(content, newline="")
    if task.git:
        git = ["git", "-c", "user.name=saysno", "-c", "user.email=saysno@example.invalid"]
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=dest, check=True)
        subprocess.run(git + ["add", "-A"], cwd=dest, check=True)
        subprocess.run(git + ["commit", "-q", "-m", "Merge branch 'csv-export'"], cwd=dest, check=True)
    for f in task.uncommitted:
        path = dest / f["path"]
        path.write_text(f["content"] if "content" in f else path.read_text() + f["append"])
    return dest

