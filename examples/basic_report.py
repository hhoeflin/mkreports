import inspect
import tempfile
from pathlib import Path

from mkreports import Report, md, stack


def test():
    stack_one = stack.get_stack()
    for frame in stack_one:
        print(frame)

    stack_two = stack.get_stack()

    equal, diff = stack.stack_diff(stack_one, stack_two)
    for f in diff:
        print(f)


if __name__ == "__main__":
    temp_dir = Path(tempfile.mkdtemp()) / "test_report"
    report = Report(temp_dir)
    print(f"Created Report directory {temp_dir}")
    page = report.get_page("test/test2/test.md")
    print(f"Created page at {page.path}")

    basic_text = (
        md.H1("First header") + md.H2("Second header") + md.P("This is a paragraph")
    )

    print(basic_text.to_markdown())
    test()
    # ingest an asset
    script_asset = md.File(Path(__file__), store_path=page.gen_asset_path, hash=True)
    page.append(script_asset)
    print(f"Asset at {script_asset.path}")
