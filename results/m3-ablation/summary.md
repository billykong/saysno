# Results

Generated from `runs.jsonl` by `python -m evals.summarize`. Do not edit by hand.

## claude-haiku-5-5 (thinking disabled, effort high; features: cache, denial-help, output-cap, trim-pipes)

**1/3 runs passed** (33%) across 1 tasks. Total cost $0.0154; 58 input and 7,770 output tokens, plus 222,905 read from and 74,277 written to the prompt cache.

Largest prompt 25,520 tokens; 12 of 20 `bash` calls denied; 6 tool outputs capped; tests ran in 2 of 3 runs.

1 of 3 runs added tests (allowed; existing tests must be kept).

| Difficulty | Passed |
| --- | --- |
| medium | 1/3 |

| Task | Difficulty | Provokes | Passed | Calls (mean) | Prompt tokens (mean) | Cost (mean) | Stops | Why runs failed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| refunds-big-file | medium | large-output | 1/3 | 8.7 | 99,080 | $0.0051 | end_turn ×3 | tests fail ×2 |

Commands denied (batch mode turns every ask into a deny):

- `python -m csvreport data/orders_2025.csv --group region --sum amount --month 2025-03` ×3
- `cd . && ls -la && find . -name "*.py" -not -path "./.git/*" | head -50 && ls data 2>/dev/null` ×2
- `python -c "from csvreport.values import parse_number as p; print(p('(241.52)'), p('(1,886.46)'), p('1,234.50'))"` ×2
- `python -m csvreport data/orders_2025.csv --group region --sum amount --month 2025-03 --where status=paid` ×2
- `cd . && ls -la && find . -path ./.git -prune -o -type f -print | head -100 && echo "---" && head -5 data/orders_2025.csv 2>/dev/null; wc -l data/orders_2025.csv 2>/dev/null` ×1
- `python -c "
import csv,collections
c=collections.Counter()
with open('data/orders_2025.csv',encoding='utf-8-sig') as f:
    for r in csv.DictReader(f): c[r['status'].strip()]+=1
print(c)"` ×1
- `python -c "
import csv,collections
r=list(csv.DictReader(open('data/orders_2025.csv',encoding='utf-8-sig')))
print(len(r), list(r[0].keys()))
for c in r[0].keys():
    vals=collections.Counter(x[c] for x in r)
    print(c, len(vals), vals.most_common(4))
"` ×1

## claude-haiku-5-5 (thinking disabled, effort high; features: cache, denial-help, steer, trim-pipes)

**0/1 runs passed** (0%) across 1 tasks. Total cost $0.1185; 16 input and 2,100 output tokens, plus 32,645 read from and 197,274 written to the prompt cache.

Largest prompt 197,276 tokens; 2 of 5 `bash` calls denied; 0 tool outputs capped; tests ran in 0 of 1 runs.

| Difficulty | Passed |
| --- | --- |
| medium | 0/1 |

| Task | Difficulty | Provokes | Passed | Calls (mean) | Prompt tokens (mean) | Cost (mean) | Stops | Why runs failed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| refunds-big-file | medium | large-output | 0/1 | 7.0 | 229,935 | $0.1185 | end_turn ×1 | tests fail ×1 |

Commands denied (batch mode turns every ask into a deny):

- `cd . && ls -R | head -50 && echo --- && python -m csvreport data/orders_2025.csv --group region --sum amount --month 2025-03 ; echo --- ; head -5 data/orders_2025.csv` ×1
- `python -m csvreport data/orders_2025.csv --group region --sum amount --month 2025-03` ×1
