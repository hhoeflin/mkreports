from mkreports import Report, md


def use_basic(report: Report) -> None:
    p = report.page("basic.md", truncate=True)

    p.H1("Basic formatting elements")

    with p.H2("Headings", anchor=(heading_anchor := md.Anchor("my-headings"))):
        p.Code(
            """
            md.H1("Header type 1")
            md.H2("Header type 2")
            md.H3("Header type 3")
            md.H4("Header type 4")
            md.H5("Header type 5")
            md.H6("Header type 6")
            md.H7("Header type 7")
            """,
            title="Available headings",
        )

    with p.H2("Lists") as p2:
        numbered_list = (
            md.List(marker="1")
            .append("First item")
            .append("Second item")
            .append("Third item")
        )
        unordered_list = md.List(("apples", "pears", "strawberry"), marker="*")

        numbered_list = numbered_list.append(
            md.Raw("Some fruit:") + unordered_list
        ).append(
            md.Raw("A code block:")
            + md.Code(
                """
                print("Hello world")                    
                """,
                title="Hello world",
                language="python",
            ),
        )

        p2.add(numbered_list)

    with p.H2("Links") as p2:
        p2.Raw(
            """
            A number of different types of links are possible. Those within
            a page to an anchor or to another page (with or without anchor)
            """
        )
        p2.P(
            "A link back to the "
            + p.md.Link(anchor=heading_anchor, text="first heading")
        )
        p2.P(
            "A link to another page "
            + p.md.Link("Images", to_page_path=report.page("images.md").path)
        )
        p2.P("Or just to any page " + p.md.Link("Google", url="https://google.com"))
        p2.P("Or of course also just straight markdown [Google](https://google.com)")
