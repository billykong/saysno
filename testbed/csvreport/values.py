"""Turn cell text into numbers and dates."""

from datetime import date, datetime


def parse_number(text):
    """'1,234.50' -> 1234.5, '(12.50)' -> -12.5, '$3' -> 3.0.

    Empty or unreadable cells ('', 'n/a') give None, so they are left out of totals.
    """
    if text is None:
        return None
    s = text.strip().replace("$", "").replace("€", "").replace("£", "")
    negative = s.startswith("(") and s.endswith(")")
    if negative:
        s = s[1:-1]
    s = s.replace(",", "")
    try:
        value = float(s)
    except ValueError:
        return None
    return -value if negative else value


def parse_date(text):
    """ISO dates (2025-03-01) or day-first dates (01/03/2025)."""
    s = text.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"not a date: {text!r}")


def month_range(month):
    """'2025-03' -> (2025-03-01, 2025-04-01): the start is included, the end is not."""
    year, m = (int(part) for part in month.split("-"))
    start = date(year, m, 1)
    end = date(year + 1, 1, 1) if m == 12 else date(year, m + 1, 1)
    return start, end
