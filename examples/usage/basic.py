from mkreports import Report, md


def use_basic(report: Report) -> None:
    with report.get_page("basic.md", append=False) as p:
        p.add(md.H1("Basic formatting elements"))

        with p.add(md.H2("Headings")):
            p.add(
                md.Code(
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
            )

        with p.add(md.H2("Lists")):
            with p.track_code():
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

            p.add(numbered_list, add_code=True)

        with p.add(md.H2("Links")):
            p.add(md.Admonition("Not yet implemented", "warning"))
