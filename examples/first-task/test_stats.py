from stats import mean, summary


def test_mean():
    assert mean([2, 4, 6]) == 4


def test_mean_empty():
    assert mean([]) is None


def test_summary_skips_blanks():
    rows = [{"price": "10"}, {"price": ""}, {"price": "20"}]
    assert summary(rows, "price") == {"count": 2, "mean": 15}
