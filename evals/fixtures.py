"""Generated data files, so large inputs are reproducible without being committed."""

import random
from datetime import date, timedelta


def orders_2025():
    """About 5,000 orders across 2025: some with thousands separators, about 5% refunds in parentheses."""
    rng = random.Random(2025)
    lines = ["date,region,product,status,amount"]
    day = date(2025, 1, 1)
    for _ in range(5000):
        day += timedelta(days=rng.random() < 0.07)
        amount = round(rng.uniform(5, 2500), 2)
        if rng.random() < 0.05:
            text, status = f"({amount:,.2f})", "refunded"
        else:
            text, status = f"{amount:,.2f}", rng.choice(["paid", "paid", "paid", "pending"])
        if "," in text:
            text = f'"{text}"'
        lines.append(f"{day},{rng.choice(['EU', 'US', 'APAC', 'LATAM'])},"
                     f"{rng.choice(['widget', 'gadget', 'gizmo', 'doohickey'])},{status},{text}")
    return "\n".join(lines) + "\n"


GENERATORS = {"orders_2025": orders_2025}
