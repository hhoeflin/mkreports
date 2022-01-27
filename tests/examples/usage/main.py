import inspect
from pathlib import Path

import mkreports
import typer
from mkreports import Report, add_pkg_docs

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
    # add the docstrings
    add_pkg_docs(
        Path(inspect.getfile(mkreports)).parent,
        parent_name="Reference",
        report=report,
    )


def main(report_dir: Path):
    report = Report(
        report_dir,
        site_name="Mkreports documentations",
    )
    run_all(report)


if __name__ == "__main__":
    typer.run(main)
