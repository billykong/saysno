"""Build a report: one row per group, sorted by group, then a TOTAL row."""

from .aggregate import aggregate, filter_rows, group_rows
from .reader import normalise
from .values import month_range, parse_date


def build_report(rows, group, metrics, where=(), month=None, date_column="date"):
    """metrics is a list of (function, column) pairs. Returns (header, body, total)."""
    group = normalise(group)
    metrics = [(function, normalise(column)) for function, column in metrics]
    date_column = normalise(date_column)
    if rows:
        for column in [group] + [column for _, column in metrics]:
            if column not in rows[0]:
                raise ValueError(f"unknown column {column!r}")

    rows = filter_rows(rows, where)
    if month:
        start, end = month_range(month)
        rows = [row for row in rows if start <= parse_date(row[date_column]) < end]

    header = [group] + [f"{function}({column})" for function, column in metrics]
    body = []
    for key, members in sorted(group_rows(rows, group).items()):
        body.append([key] + [aggregate(function, [m.get(column) for m in members])
                             for function, column in metrics])
    total = ["TOTAL"] + [aggregate(function, [row.get(column) for row in rows])
                         for function, column in metrics]
    return header, body, total
