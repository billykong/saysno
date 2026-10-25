"""csvreport FILE --group COLUMN --sum COLUMN [--mean COLUMN ...] [--where COL=VALUE] [--month YYYY-MM]"""

import argparse
import sys

from .aggregate import FUNCTIONS
from .formats import RENDERERS
from .reader import read_rows
from .report import build_report


def main(argv=None):
    parser = argparse.ArgumentParser(prog="csvreport")
    parser.add_argument("file")
    parser.add_argument("--group", required=True, help="column to group by")
    for function in FUNCTIONS:
        parser.add_argument(f"--{function}", action="append", default=[], metavar="COLUMN")
    parser.add_argument("--where", action="append", default=[], metavar="COLUMN=VALUE")
    parser.add_argument("--month", metavar="YYYY-MM", help="keep rows dated in this month")
    parser.add_argument("--date-column", default="date")
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--format", choices=RENDERERS, default="text")
    args = parser.parse_args(argv)

    metrics = [(function, column) for function in FUNCTIONS for column in getattr(args, function)]
    if not metrics:
        parser.error("give at least one of " + ", ".join(f"--{f}" for f in FUNCTIONS))
    rows = read_rows(args.file, args.delimiter)
    try:
        header, body, total = build_report(rows, args.group, metrics, args.where, args.month, args.date_column)
    except ValueError as e:
        parser.error(str(e))
    sys.stdout.write(RENDERERS[args.format](header, body, total))


if __name__ == "__main__":
    main()
