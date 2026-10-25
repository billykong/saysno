from datetime import date

from csvreport.values import month_range, parse_date, parse_number


def test_plain_numbers_and_currency():
    assert parse_number("120.00") == 120.0
    assert parse_number(" $3 ") == 3.0


def test_unreadable_cells_are_none():
    assert parse_number("") is None
    assert parse_number("n/a") is None
    assert parse_number(None) is None


def test_iso_dates():
    assert parse_date("2025-03-01") == date(2025, 3, 1)


def test_month_range():
    assert month_range("2025-03") == (date(2025, 3, 1), date(2025, 4, 1))
