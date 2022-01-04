from pathlib import Path

from mkreports import Report

from .basic import use_basic
from .code_blocks import use_code_blocks
from .images import use_images
from .tables import use_tables


def run_all(report: Report):
    use_basic(report)
    # documentation for images
    use_images(report)
    # documentation for tables
    use_tables(report)
    # documentation for code blocks
    use_code_blocks(report)


if __name__ == "__main__":
    report = Report(Path("usage_docs"), site_name="Mkreports documentations")
    run_all(report)
