from pathlib import Path

from csvreport.cli import main

SALES = Path(__file__).parent.parent / "data" / "sales.csv"


def test_names_with_spaces_and_capitals(capsys):
    main([str(SALES), "--group", "Sales Region", "--sum", "Unit Price", "--where", "Order Status=paid",
          "--date-column", "Order Date", "--month", "2025-03", "--format", "csv"])
    assert capsys.readouterr().out == "sales region,sum(unit price)\nNorth,14.50\nSouth,20.00\nTOTAL,34.50\n"


def test_extra_spaces_in_arguments(capsys):
    main([str(SALES), "--group", " sales   REGION ", "--count", "unit  price", "--format", "csv"])
    assert capsys.readouterr().out == "sales region,count(unit price)\nNorth,3\nSouth,2\nTOTAL,5\n"
