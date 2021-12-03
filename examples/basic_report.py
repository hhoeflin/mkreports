import inspect
import tempfile
from pathlib import Path

from mkreports import Report, md, stack


def test():
    stack_here = stack.get_stack()
    for frame in stack_here:
        print(frame)


if __name__ == "__main__":
    temp_dir = Path(tempfile.mkdtemp()) / "test_report"
    report = Report(temp_dir)
    print(f"Created Report directory {temp_dir}")
    page = report.get_page("test/test2/test.md")
    print(f"Created page at {page.path}")

    basic_text = (
        md.H1("First header") + md.H2("Second header") + md.P("This is a paragraph")
    )

    print(basic_text.process_all())
    test()
    # ingest an asset
    asset_path = Path(__file__)
    ingested_asset_path = page.ingest_asset(asset_path)
    print(f"Ingested asset into path {ingested_asset_path}")
