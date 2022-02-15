from mkreports import Report


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def use_code_blocks(report: Report) -> None:
    """
    Show different ways on how code blacks can be included.
    """
    p = report.page("code_blocks.md", truncate=True)
    p.H1("Code blocks")

    with p.H2("Tracking code (tabbed)"):
        p.Raw(
            """
            One of the features of mkreports is that we can include
            code right from the script into the output. This is done by 
            starting a context manager and all code in the 
            scope of the context manager will be recorded.
            """
        )

        x = 3
        a = fib(x)

        p.P(f"fib({x}) = {a}")

        p.P(
            """
            By default, the **tabbed** version will be used, but there
            are also the options

            - **top-c**: Collapsed code block at the top
            - **top-o**: Open code block at the top
            - **bottom-c**: Collapsed code block at the bottom
            - **bottom-o**: Open code block at the bottom

            The default style can be set when creating the page using the 
            `code_layout` parameter, but can also be set one at a time later
            using the `ctx` method on a page.
                """
        )

    with p.H2("Tracking code (top-c)").ctx(layout="top-c"):
        p.P("The code as a collapsed admonition before the output.")
        x = 4
        a = fib(x)

        p.P(f"fib({x}) = {a}")

    with p.H2("Tracking code (top-o)").ctx(layout="top-o"):
        p.P("The code as an open code block before the output.")
        x = 5
        a = fib(x)

        p.P(f"fib({x}) = {a}")

    with p.H2("Tracking code (bottom-c)").ctx(layout="bottom-c"):
        p.P("The code as a collapsed admoniton after the output.")
        x = 6
        a = fib(x)

        p.Raw(f"fib({x}) = {a}")

    with p.H2("Tracking code (bottom-o)").ctx(layout="bottom-o"):
        p.P("The code as an open code block after the output.")
        x = 7
        a = fib(x)

        p.P(f"fib({x}) = {a}")

    with p.H2("Adding code files"):
        p.P(
            """
            In addtion we can also add entire code files, for 
            example at the end of a page the file or files that 
            created a page. This can be wrapped into a collapsed
            admonition so that the file is hidden.
            """
        )

        p.CollapsedCodeFile(__file__)

    p.P(
        """
        And at the end will add another copy of the code-file, 
        but automatically when ending the page context manager.
        """
    )
