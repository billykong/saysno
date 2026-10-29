import pytest

from saysno.policy import check, decide


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


@pytest.mark.parametrize("command", [
    "python -m pytest -q 2>&1 | tail -5", "pytest 2>&1", "ls -R | head -100", "git log | head", "cat a.csv | tail -n 20",
])
def test_trim_endings_run_without_asking_when_switched_on(command):
    # F-02: Haiku trims its own output; these endings can't start a second command.
    assert check("bash", {"command": command})[0] == "ask"
    assert check("bash", {"command": command}, trim=True) == ("allow", None)


@pytest.mark.parametrize("command", [
    "cat x | sh", "ls | head -5 | sh", "ls | tail | head", "rm x 2>&1 | tail", "ls; rm x | head", "ls | head -c 5",
])
def test_trim_endings_do_not_hide_a_second_command(command):
    assert check("bash", {"command": command}, trim=True)[0] == "ask"


def test_ask_says_why():
    # T-06: the reason goes into the denial.
    assert "';'" in check("bash", {"command": "ls; rm x"})[1]
    assert "'rm' is not on the allow list" in check("bash", {"command": "rm x"})[1]
