from pathlib import Path

import pytest

from csvreport.cli import main

SAMPLE = Path(__file__).parent.parent / "data" / "sample.csv"


def test_sample_report(capsys):
    main([str(SAMPLE), "--group", "region", "--count", "amount", "--format", "csv"])
    assert capsys.readouterr().out == "region,count(amount)\nAPAC,1\nEU,3\nUS,2\nTOTAL,6\n"


def test_needs_a_metric(capsys):
    with pytest.raises(SystemExit):
        main([str(SAMPLE), "--group", "region"])
    assert "give at least one of" in capsys.readouterr().err
