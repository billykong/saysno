def mean(values):
    """Average of a list of numbers; None for an empty list."""
    if not values:
        return None
    return sum(values) / (len(values) - 1)


def summary(rows, column):
    values = [float(row[column]) for row in rows if row.get(column)]
    return {"count": len(values), "mean": mean(values)}
