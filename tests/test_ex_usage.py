"""
Test the usage examples.

Here we use the usage examples to perform a regression test.
A gold-standard output will be stored to which the
new output will be compared. This way any changes can
be detected.
"""

from pathlib import Path

from mkreports import Report

from dircmp import DirCmp
from examples.usage.main import run_all

gold_path_all = Path(__file__).parent / "test_ex_usage" / "all"


def test_all(replace_gold, tmp_path):
    """Test basic usage example."""
    dircmp = DirCmp(tmp_path, gold_path_all, replace_gold)
    report = Report(dircmp.test_output_dir, site_name="Mkreports documentations")
    run_all(report)
    assert dircmp.is_same, dircmp.report_full_closure()
