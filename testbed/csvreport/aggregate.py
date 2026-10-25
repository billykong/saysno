"""Filter, group and aggregate rows."""

from .reader import normalise
from .values import parse_number

FUNCTIONS = ("sum", "mean", "median", "count", "min", "max")


def filter_rows(rows, conditions):
    """Keep rows matching every 'column=value' condition (values compared case-insensitively)."""
    parsed = []
    for condition in conditions:
        column, _, value = condition.partition("=")
        parsed.append((normalise(column), value.strip().lower()))
    return [row for row in rows
            if all(row.get(column, "").strip().lower() == value for column, value in parsed)]


def group_rows(rows, column):
    groups = {}
    for row in rows:
        groups.setdefault(row.get(column, "").strip(), []).append(row)
    return groups


def mean(values):
    return sum(values) / len(values) if values else None


def median(values):
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def aggregate(function, cells):
    """Apply one function to a column's cells. count counts non-empty cells;
    the others use the cells that read as numbers."""
    if function == "count":
        return sum(1 for cell in cells if cell and cell.strip())
    numbers = [n for n in (parse_number(cell) for cell in cells) if n is not None]
    if function == "sum":
        return float(sum(numbers))
    if function == "mean":
        return mean(numbers)
    if function == "median":
        return median(numbers)
    if function in ("min", "max"):
        return (min if function == "min" else max)(numbers) if numbers else None
    raise ValueError(f"unknown function {function!r}")
