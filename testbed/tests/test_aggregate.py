from csvreport.aggregate import aggregate, filter_rows, group_rows, mean, median

ROWS = [{"region": "EU", "status": "Paid"}, {"region": "US", "status": "paid"}, {"region": "EU", "status": "pending"}]


def test_filter_is_case_insensitive():
    assert filter_rows(ROWS, ["Status=PAID"]) == ROWS[:2]


def test_group_rows():
    assert list(group_rows(ROWS, "region")) == ["EU", "US"]


def test_mean():
    assert mean([1, 2, 6]) == 3
    assert mean([]) is None


def test_median_odd():
    assert median([3, 1, 2]) == 2


def test_median_even():
    assert median([4, 1, 3, 2]) == 2.5


def test_count_counts_non_empty_cells():
    assert aggregate("count", ["1", "", " ", "x", None]) == 2


def test_min_max_of_nothing():
    assert aggregate("min", ["", "n/a"]) is None
    assert aggregate("max", ["1", "7", "3"]) == 7.0
