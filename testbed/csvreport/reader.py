"""Read a CSV file into a list of dicts keyed by normalised column name."""

import csv


def normalise(name):
    """'  Unit  Price ' -> 'unit price'. Column names are matched in this form."""
    return " ".join(name.split()).lower()


def read_rows(path, delimiter=","):
    # utf-8-sig drops the byte-order mark that Excel writes at the start of the file.
    with open(path, newline="", encoding="utf-8-sig") as f:
        records = csv.reader(f, delimiter=delimiter)
        header = [normalise(name) for name in next(records)]
        rows = []
        for record in records:
            if not any(cell.strip() for cell in record):
                continue  # blank line
            rows.append(dict(zip(header, record)))
    return rows
