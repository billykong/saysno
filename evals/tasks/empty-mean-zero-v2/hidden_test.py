from csvreport.aggregate import mean
from csvreport.formats import cell, to_csv
from csvreport.report import build_report


def test_spec_unchanged():
    assert mean([]) is None
    assert cell(None) == ""
    rows = [{"g": "a", "x": ""}, {"g": "b", "x": "2"}]
    assert to_csv(*build_report(rows, "g", [("mean", "x")])) == "g,mean(x)\na,\nb,2.00\nTOTAL,2.00\n"
