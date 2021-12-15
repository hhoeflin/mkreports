from pathlib import Path

from mkreports import Report, md, stack

if __name__ == "__main__":
    stack_start = stack.get_stack()
    report = Report("basic_report", site_name="Basic report")
    print(f"Created Report directory {report.path}")
    page = report.get_page("test/test2/test.md", append=False)
    print(f"Created page at {page.path}")

    basic_text = (
        md.H1("First header") + md.H2("Second header") + md.P("This is a paragraph")
    )

    print(basic_text.to_markdown())
    # ingest an asset
    script_asset = md.File(Path(__file__), store_path=page.gen_asset_path, hash=True)
    mkdocs_img = md.ImageFile(
        Path(__file__).parent / "mkdocs.jpg", store_path=page.gen_asset_path, hash=True
    )
    page.append(basic_text)
    page.append(mkdocs_img)

    # and now we append a ggplot image
    from plotnine import aes, facet_wrap, geom_point, ggplot, stat_smooth
    from plotnine.data import mtcars

    page.append(
        md.Image(
            ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
            + geom_point()
            + stat_smooth(method="lm")
            + facet_wrap("~gear"),
            store_path=page.gen_asset_path,
        )
    )

    # the table as markdown
    page.append(md.Table(mtcars, index=False))

    # and as a DataTable
    page.append(md.DataTable(mtcars, store_path=page.gen_asset_path))

    print(f"Asset at {script_asset.path}")
    print(f"Image at {mkdocs_img.path}")
    print(f"Page at {page.path}")

    # now we want to print a little code
    stack_end = stack.get_stack()
    diff_equal, diff_diff = stack.stack_diff(stack_start, stack_end)
    page.append(diff_diff[0].md_code())
