from pathlib import Path

from csvreport.cli import main
from csvreport.reader import read_rows

EXPORT = Path(__file__).parent.parent / "data" / "export.csv"


def test_bom_dropped():
    assert list(read_rows(EXPORT)[0]) == ["date", "region", "amount"]


def test_group_by_first_column(capsys):
    main([str(EXPORT), "--group", "date", "--sum", "amount", "--format", "csv"])
    assert capsys.readouterr().out == "date,sum(amount)\n2025-03-01,30.00\n2025-03-02,5.00\nTOTAL,35.00\n"
