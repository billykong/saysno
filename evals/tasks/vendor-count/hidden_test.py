from pathlib import Path

from csvreport.cli import main
from csvreport.reader import read_rows

VENDORS = Path(__file__).parent.parent / "data" / "vendors.csv"


def test_rows_with_empty_first_cell_kept():
    assert len(read_rows(VENDORS)) == 6


def test_vendor_count(capsys):
    main([str(VENDORS), "--group", "region", "--count", "amount", "--format", "csv"])
    assert capsys.readouterr().out == "region,count(amount)\nEU,4\nUS,2\nTOTAL,6\n"
