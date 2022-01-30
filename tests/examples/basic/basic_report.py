from pathlib import Path

from mkreports import Report, md, stack

if __name__ == "__main__":
    stack_start = stack.get_stack()
    report = Report("basic_report", site_name="Basic report")
    print(f"Created Report directory {report.path}")
    page = report.page("test/test2/test.md", append=False)
    print(f"Created page at {page.path}")

    basic_text = (
        md.H1("First header") + md.H2("Second header") + md.P("This is a paragraph")
    )

    print(basic_text.to_markdown())
    # ingest an asset
    script_asset = md.File(
        Path(__file__), store_path=page.gen_asset_path, use_hash=True
    )
    mkdocs_img = md.ImageFile(
        Path(__file__).parent / "mkdocs.jpg",
        store_path=page.gen_asset_path,
        use_hash=True,
    )
    page.add(basic_text)
    page.add(mkdocs_img)

    # and now we append a ggplot image
    from plotnine import aes, facet_wrap, geom_point, ggplot, stat_smooth
    from plotnine.data import mtcars

    page.add(
        md.Image(
            ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
            + geom_point()
            + stat_smooth(method="lm")
            + facet_wrap("~gear"),
            store_path=page.gen_asset_path,
        )
    )

    # the table as markdown
    page.add(md.Table(mtcars, index=False))

    # and as a DataTable
    page.add(md.DataTable(mtcars, store_path=page.gen_asset_path))

    print(f"Asset at {script_asset.path}")
    print(f"Image at {mkdocs_img.path}")
    print(f"Page at {page.path}")

    # now we want to print a little code
    stack_end = stack.get_stack()
    page.add(stack.StackDiff(stack_start, stack_end).changed[0].md_code())

    page.add(md.H2("Several different containers"))
    # and now we want to add an admonition
    stack_end2 = stack.get_stack()
    page.add(
        md.Admonition(
            stack.StackDiff(stack_end, stack_end2).changed[0].md_code()
            + "This is an admonition",
            kind="bug",
            collapse=True,
        )
    )

    page.add(md.Tab("A test text", "Title 1") + md.Tab("Second test", "Title 2"))

    page.add(md.H2("A stack as tabs"))
    page.add(stack.stack_to_tabs(stack_end2))
