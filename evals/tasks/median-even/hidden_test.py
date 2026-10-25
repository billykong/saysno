from csvreport.aggregate import median


def test_median():
    assert median([4, 1, 3, 2]) == 2.5
    assert median([5, 1]) == 3
    assert median([3, 1, 2]) == 2
