import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from loc import count  # noqa: E402

M1_BUDGET = 200


def test_agent_fits_the_m1_line_budget():
    # PRD L-03: enforced at M1, reported afterwards.
    assert count(Path(__file__).parent.parent / "saysno") <= M1_BUDGET
