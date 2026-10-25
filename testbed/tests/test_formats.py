from csvreport.formats import cell, to_csv, to_markdown, to_text

HEADER = ["region", "sum(amount)", "count(amount)"]
BODY = [["EU", 80.0, 3], ["US", 1234.5, 1]]
TOTAL = ["TOTAL", 1314.5, 4]


def test_cell():
    assert cell(None) == ""
    assert cell(3) == "3"
    assert cell(1.0) == "1.00"
    assert cell("EU") == "EU"


def test_rounding_half_up():
    assert cell(2.675) == "2.68"
    assert cell(0.125) == "0.13"


def test_text():
    assert to_text(HEADER, BODY, TOTAL) == (
        "region  sum(amount)  count(amount)\n"
        "------  -----------  -------------\n"
        "EU            80.00              3\n"
        "US          1234.50              1\n"
        "------  -----------  -------------\n"
        "TOTAL       1314.50              4\n"
    )


def test_csv():
    assert to_csv(HEADER, BODY, TOTAL) == (
        "region,sum(amount),count(amount)\nEU,80.00,3\nUS,1234.50,1\nTOTAL,1314.50,4\n"
    )


def test_markdown():
    assert to_markdown(HEADER, BODY, TOTAL) == (
        "| region | sum(amount) | count(amount) |\n"
        "| --- | --- | --- |\n"
        "| EU | 80.00 | 3 |\n"
        "| US | 1234.50 | 1 |\n"
        "| **TOTAL** | 1314.50 | 4 |\n"
    )


def test_markdown_escapes_pipes():
    out = to_markdown(["product", "count(x)"], [["a|b", 1]], ["TOTAL", 1])
    assert "| a\\|b | 1 |" in out


def test_empty_values_render_blank():
    assert to_csv(["g", "mean(x)"], [["a", None]], ["TOTAL", None]) == "g,mean(x)\na,\nTOTAL,\n"
