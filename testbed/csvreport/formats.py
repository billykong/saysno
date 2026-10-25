"""Render a report as an aligned text table, CSV or Markdown."""

import csv
import io
from decimal import ROUND_HALF_UP, Decimal


def cell(value):
    """None -> ''; whole counts as they are; other numbers to 2 places, rounded half up."""
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return str(value)


def to_text(header, body, total):
    table = [header] + [[cell(v) for v in row] for row in body + [total]]
    widths = [max(len(str(row[i])) for row in table) for i in range(len(header))]
    lines = []
    for n, row in enumerate(table):
        parts = [str(v).ljust(w) if i == 0 else str(v).rjust(w) for i, (v, w) in enumerate(zip(row, widths))]
        lines.append("  ".join(parts).rstrip())
        if n == 0 or n == len(table) - 2:
            lines.append("  ".join("-" * w for w in widths))
    return "\n".join(lines) + "\n"


def to_csv(header, body, total):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    for row in body + [total]:
        writer.writerow([cell(v) for v in row])
    return out.getvalue()


def to_markdown(header, body, total):
    def line(values):
        return "| " + " | ".join(str(v).replace("|", "\\|") for v in values) + " |"

    lines = [line(header), "|" + "|".join(" --- " for _ in header) + "|"]
    lines += [line([cell(v) for v in row]) for row in body]
    lines.append(line(["**TOTAL**"] + [cell(v) for v in total[1:]]))
    return "\n".join(lines) + "\n"


RENDERERS = {"text": to_text, "csv": to_csv, "md": to_markdown}
