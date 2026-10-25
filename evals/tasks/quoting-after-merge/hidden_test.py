from csvreport.formats import to_csv


def test_minimal_quoting():
    assert to_csv(["g", "sum(x)"], [["a,b", 1.0]], ["TOTAL", 1.0]) == 'g,sum(x)\n"a,b",1.00\nTOTAL,1.00\n'
