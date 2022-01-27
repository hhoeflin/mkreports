from mkreports import Report, md


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
    with report.get_page("code_blocks.md", append=False) as p:
        p.add(md.H1("Code blocks"))

        with p.add(md.H2("Tracking code")):
            p.add(
                """
                One of the features of mkreports is that we can include
                code right from the script into the output. Not only does
                this include the code block in the script itself, but
                also the source of functions that are called in the block. 
                Here as an example, the fibonacci sequence. 

                This is enabled by the `track_code` method that is part of 
                a page object and functions as a context manager which installs
                a tracing function, recording
                the code and all called functions and their source code. 

                A code block that has been tracked can then be included
                when adding a markdown object to a page by usig the 
                `add_code=True` parameter. This is then combined with 
                the markdown object by adding tabs (the markdown object 
                active under the 'Content' tab and the code block under 'Code').
                """
            )

            with p.track_code():
                x = 3
                a = fib(x)

            p.add(f"fib({x}) = {a}", add_code=True)

        with p.add(md.H2("Relative to position")):
            p.add(
                """
                In addition to tracking code as shown above, we can also
                refer to code blocks as either 
                - the context around the current statement
                - A number of statements around the current one. 
                """
            )

            p.add(md.Admonition("This is not yet implemented", kind="warning"))