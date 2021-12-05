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
    report = Report("basic_report", site_name="Basic report")
    print(f"Created Report directory {report.path}")
    page = report.get_page("test/test2/test.md")
    print(f"Created page at {page.path}")

    basic_text = (
        md.H1("First header") + md.H2("Second header") + md.P("This is a paragraph")
    )

    print(basic_text.to_markdown())
    test()
    # ingest an asset
    script_asset = md.File(Path(__file__), store_path=page.gen_asset_path, hash=True)
    mkdocs_img = md.ImageFile(
        Path(__file__).parent / "mkdocs.jpg", store_path=page.gen_asset_path, hash=True
    )
    page.append(basic_text)
    page.append(mkdocs_img)
    print(f"Asset at {script_asset.path}")
    print(f"Image at {mkdocs_img.path}")
    print(f"Page at {page.path}")
