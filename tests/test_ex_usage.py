"""
Test the usage examples.

Here we use the usage examples to perform a regression test.
A gold-standard output will be stored to which the
new output will be compared. This way any changes can
be detected.
"""

import sys
from pathlib import Path

sys.path.insert(1, str(Path(__file__).parents[1] / "docs"))
import filecmp

from mkreports import Report
from staging.main import run_all

from dircmp import cmp_dirs_recursive

gold_path = Path(__file__).parents[1] / "docs/final"


def test_all(tmp_path, ignore_images):
    """Test basic usage example."""
    if ignore_images:
        ignore = [
            Path("site"),
            Path("docs/usage/images.md"),
            Path("docs/quickstart.md"),
            Path("docs/usage/images_store"),
            Path("docs/quickstart_store"),
        ]
    else:
        ignore = [Path("site")]
    report = Report.create(tmp_path, report_name="Mkreports documentations")
    run_all(report)

    if not cmp_dirs_recursive(tmp_path, gold_path, ignore):
        filecmp.dircmp(tmp_path, gold_path).report_full_closure()
        raise AssertionError("Directories not equal")
