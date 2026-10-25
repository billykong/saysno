from datetime import date
from pathlib import Path

from csvreport.cli import main
from csvreport.values import parse_date

MARCH = Path(__file__).parent.parent / "data" / "march_2025.csv"


def test_day_first():
    assert parse_date("05/03/2025") == date(2025, 3, 5)
    assert parse_date("25/12/2025") == date(2025, 12, 25)


def test_march_report(capsys):
    main([str(MARCH), "--group", "region", "--sum", "amount", "--month", "2025-03", "--format", "csv"])
    assert capsys.readouterr().out == "region,sum(amount)\nAPAC,100.00\nEU,140.00\nUS,270.00\nTOTAL,510.00\n"
