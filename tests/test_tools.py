import pytest

from saysno.tools import ToolError, Tools


@pytest.fixture
def tools(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\ny = 2\nx = 1\n")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.py").write_text("def f():\n    return 'needle'\n")
    return Tools(tmp_path)


def test_read_file_numbers_lines_and_says_what_is_left(tools):
    out = tools.run("read_file", {"path": "a.py", "offset": 2, "limit": 1})
    assert out == "     2\ty = 2\n(1 more lines; read again with a higher offset)"


def test_edit_file_replaces_a_unique_match(tools):
    assert tools.run("edit_file", {"path": "a.py", "old": "y = 2", "new": "y = 3"}) == "edited a.py"
    assert (tools.root / "a.py").read_text() == "x = 1\ny = 3\nx = 1\n"


@pytest.mark.parametrize("old,count", [("z = 9", 0), ("x = 1", 2), ("", 0)])
def test_edit_file_fails_unless_exactly_one_match(tools, old, count):
    with pytest.raises(ToolError, match=f"found {count} times"):
        tools.run("edit_file", {"path": "a.py", "old": old, "new": "q"})
    assert (tools.root / "a.py").read_text() == "x = 1\ny = 2\nx = 1\n"


@pytest.mark.parametrize("path", ["../outside.txt", "/etc/passwd", "sub/../../x"])
def test_paths_outside_the_project_are_refused(tools, path):
    with pytest.raises(ToolError, match="outside the project"):
        tools.run("read_file", {"path": path})


def test_grep_reports_path_and_line(tools):
    assert tools.run("grep", {"pattern": "needle"}) == "sub/b.py:2:    return 'needle'"
    assert tools.run("grep", {"pattern": "nothing-here"}) == "no matches"


def test_bash_runs_in_the_project_with_exit_code(tools):
    assert tools.run("bash", {"command": "ls sub"}) == "exit code 0\nb.py\n"
    assert tools.run("bash", {"command": "exit 3"}).startswith("exit code 3")


def test_bad_input_is_a_tool_error(tools):
    with pytest.raises(ToolError):
        tools.run("read_file", {"path": "missing.py"})
    with pytest.raises(ToolError):
        tools.run("read_file", {"nope": 1})
    with pytest.raises(ToolError):
        tools.run("delete_everything", {})
