from datetime import date

from csvreport.values import month_range


def test_december():
    assert month_range("2025-12") == (date(2025, 12, 1), date(2026, 1, 1))
    assert month_range("2025-11") == (date(2025, 11, 1), date(2025, 12, 1))
