import pytest

from csvreport.report import build_report

ROWS = [
    {"date": "2025-03-01", "region": "EU", "amount": "10", "status": "paid"},
    {"date": "2025-03-15", "region": "US", "amount": "20", "status": "paid"},
    {"date": "2025-03-20", "region": "EU", "amount": "30", "status": "pending"},
    {"date": "2025-04-02", "region": "EU", "amount": "40", "status": "paid"},
]


def test_group_and_total():
    header, body, total = build_report(ROWS, "region", [("sum", "amount"), ("count", "amount")])
    assert header == ["region", "sum(amount)", "count(amount)"]
    assert body == [["EU", 80.0, 3], ["US", 20.0, 1]]
    assert total == ["TOTAL", 100.0, 4]


def test_where_and_month():
    _, body, total = build_report(ROWS, "region", [("sum", "amount")], where=["status=paid"], month="2025-03")
    assert body == [["EU", 10.0], ["US", 20.0]]
    assert total == ["TOTAL", 30.0]


def test_unknown_column():
    with pytest.raises(ValueError, match="unknown column 'price'"):
        build_report(ROWS, "region", [("sum", "price")])
