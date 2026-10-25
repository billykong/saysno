from csvreport.reader import normalise, read_rows


def test_normalise():
    assert normalise("  Unit  Price ") == "unit price"


def test_read_rows(tmp_path):
    path = tmp_path / "in.csv"
    path.write_text("Region, Amount \nEU,1\n\nUS,2\n")
    assert read_rows(path) == [{"region": "EU", "amount": "1"}, {"region": "US", "amount": "2"}]


def test_other_delimiters(tmp_path):
    path = tmp_path / "in.csv"
    path.write_text("region;amount\nEU;1\n")
    assert read_rows(path, ";") == [{"region": "EU", "amount": "1"}]
