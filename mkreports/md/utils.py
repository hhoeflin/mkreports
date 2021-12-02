from typing import Optional


def ensure_newline(x: str, nl_before: int, nl_after: int) -> str:
    """Ensure that the number of newlines is as requested."""
    # first strip trailing newline, then add requested number
    x_no_nl = x.rstrip("\n").lstrip("\n")
    return "\n" * nl_before + x_no_nl + "\n" * nl_after


def count_newlines(x: str, before=True) -> int:
    """
    Count the number of newlines from front or back.

    Here all newlines are counted while ignoring whitespace.
    Stop at first character that is not newline or whitespace.
    """
    num_nl = 0
    whitespace = [" ", "\r", "\t"]
    y = x if before else reversed(x)
    for ch in y:
        if ch == "\n":
            num_nl += 1
        elif ch in whitespace:
            continue
        else:
            return num_nl
    return num_nl
