---
{}
---

```python title="main.py"
import inspect
import shutil
from pathlib import Path

import mkreports
import typer
from mkreports import Report, add_pkg_docs

from .basic import use_basic
from .code_blocks import use_code_blocks
from .images import use_images
from .quickstart import do_quickstart
from .tables import use_tables


def add_md_pages(report: Report):
    """
    Add pages written in pure markdown format.
    """
    # open the page, and copy the other one over it
    index_page = report.page("index.md")
    shutil.copy(Path(__file__).parent / "index.md", index_page.path)

    markdown_page = report.page("markdown.md")
    shutil.copy(Path(__file__).parent / "markdown.md", markdown_page.path)


def add_code_pages(report: Report, code_dir: Path):
    for code_file in code_dir.glob("**/*.py"):
        rel_code_file = code_file.relative_to(code_dir)
        site_file_name = "site_code" / rel_code_file.with_suffix(".md")
        p = report.page(site_file_name)

        with code_file.open("r") as f:
            p.Code(f.read(), language="python", title=str(rel_code_file))


def run_all(report: Report):
    do_quickstart(report)
    add_md_pages(report)
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
    add_code_pages(report, Path(__file__).parent)


def main(report_dir: Path):
    report = Report.create(
        report_dir, report_name="Mkreports documentations", exist_ok=True
    )
    run_all(report)


if __name__ == "__main__":
    typer.run(main)

```
