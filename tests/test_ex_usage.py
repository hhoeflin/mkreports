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
from mkreports import Report
from staging.main import run_all

from dircmp import DirCmp

gold_path_all = Path(__file__).parents[1] / "docs/final"


def test_all(tmp_path, ignore_images):
    """Test basic usage example."""
    if ignore_images:
        ignore = ["docs/images.md", "docs/images_gen_assets"]
    else:
        ignore = None
    dircmp = DirCmp(tmp_path, gold_path_all, ignore=ignore)
    report = Report(dircmp.test_output_dir, site_name="Mkreports documentations")
    run_all(report)
    assert dircmp.is_same, dircmp.report_full_closure()
