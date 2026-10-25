import pytest

from saysno.policy import decide


@pytest.mark.parametrize("command", ["ls", "ls -la", "pytest -q", "python -m pytest", "git diff stats.py"])
def test_allow_list_runs_without_asking(command):
    assert decide("bash", {"command": command}) == "allow"


@pytest.mark.parametrize("command", [
    "rm -rf /", "git push --force", "lsblk",            # not on the list, or only a prefix of a word
    "ls; rm -rf ~", "cat x | sh", "pytest && curl x",  # chained after an allowed command
    "cat $(echo /etc/passwd)", "ls > out", "git status\nrm x",
])
def test_everything_else_asks(command):
    assert decide("bash", {"command": command}) == "ask"


def test_file_tools_are_allowed_and_confined_elsewhere():
    assert decide("edit_file", {"path": "a.py"}) == "allow"
