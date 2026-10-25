from pathlib import Path

from csvreport.cli import main
from csvreport.values import parse_number

SAMPLE = Path(__file__).parent.parent / "data" / "sample.csv"


def test_thousands():
    assert parse_number("1,234.50") == 1234.5
    assert parse_number("$12,000") == 12000.0


def test_sample_totals(capsys):
    main([str(SAMPLE), "--group", "region", "--sum", "amount", "--format", "csv"])
    assert capsys.readouterr().out == "region,sum(amount)\nAPAC,75.50\nEU,110.25\nUS,1149.99\nTOTAL,1335.74\n"
