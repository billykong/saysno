# csvreport

Group, filter and total CSV files into small reports.

```bash
python -m csvreport data/sample.csv --group region --sum amount --count amount
python -m csvreport data/sample.csv --group product --mean amount --where status=paid --month 2025-03 --format md
```

- Numbers may use thousands separators (`1,234.50`), currency signs, and parentheses for negatives (`(40.00)`). Unreadable cells are left out.
- Dates are ISO (`2025-03-01`) or day-first (`01/03/2025`). `--month` keeps rows from that month.
- Column names match ignoring case and extra spaces.
- Formats: `text` (default), `csv`, `md`.

Run the tests with `python -m pytest`.
