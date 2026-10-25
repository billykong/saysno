from pathlib import Path

from csvreport.cli import main
from csvreport.values import parse_number

SAMPLE = Path(__file__).parent.parent / "data" / "sample.csv"


def test_parentheses_are_negative():
    assert parse_number("(12.50)") == -12.5
    assert parse_number("($1,000.00)") == -1000.0


def test_sample_refund_subtracted(capsys):
    main([str(SAMPLE), "--group", "region", "--sum", "amount", "--format", "csv"])
    assert "EU,110.25" in capsys.readouterr().out
