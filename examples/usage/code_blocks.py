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
        with p.track_code():
            a = fib(3)

        p.add(f"fib(5) = {a}", add_code=True)
