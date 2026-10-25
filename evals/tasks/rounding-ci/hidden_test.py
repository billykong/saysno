from csvreport.formats import cell


def test_half_up():
    assert cell(2.675) == "2.68"
    assert cell(1.005) == "1.01"
    assert cell(0.125) == "0.13"
