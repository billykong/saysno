from csvreport.formats import to_markdown


def test_pipes_escaped():
    out = to_markdown(["product", "count(x)"], [["a|b", 1]], ["TOTAL", 1])
    assert out.splitlines()[2] == "| a\\|b | 1 |"
