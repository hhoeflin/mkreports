from typing import Any, Optional, Union

Text = Union[str, "SpacedText"]


def get_req_before(x: Text) -> int:
    if isinstance(x, str):
        return 0
    else:
        return x.req_nl_before


def get_req_after(x: Text) -> int:
    if isinstance(x, str):
        return 0
    else:
        return x.req_nl_after


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


def get_text(x: Text) -> str:
    if isinstance(x, str):
        return x
    else:
        return x.text


def needed_nl_between(first: Text, second: Text) -> int:
    """
    Calculates the number of newlines needed between two text objects.
    """
    if isinstance(first, str):
        req_first_after = 0
        num_first_after = count_newlines(first, before=False)
    else:
        req_first_after = first.req_nl_after
        num_first_after = count_newlines(first.text, before=False)

    if isinstance(second, str):
        req_second_before = 0
        num_second_before = count_newlines(second, before=True)
    else:
        req_second_before = second.req_nl_before
        num_second_before = count_newlines(second.text, before=True)

    add_between = max(
        max(req_first_after, req_second_before) - num_second_before - num_first_after,
        0,
    )
    return add_between


class SpacedText:
    """Representation of text with spaces before or after."""

    def __init__(self, text: str, req_nl_before: int, req_nl_after: int) -> None:
        self.text = text
        self.req_nl_before = req_nl_before
        self.req_nl_after = req_nl_after

    def __str__(self) -> str:
        return self.format_text("", "")

    def __eq__(self, other: Any) -> bool:
        if type(self) != type(other):
            return False
        return (
            self.text == other.text
            and self.req_nl_before == other.req_nl_before
            and self.req_nl_after == other.req_nl_after
        )

    def __add__(self, follow: Text) -> "SpacedText":
        add_nl = needed_nl_between(self, follow)
        return SpacedText(
            self.text + "\n" * add_nl + get_text(follow),
            self.req_nl_before,
            get_req_after(follow),
        )

    def __radd__(self, precede: Text) -> "SpacedText":
        add_nl = needed_nl_between(precede, self)
        return SpacedText(
            get_text(precede) + "\n" * add_nl + self.text,
            get_req_before(precede),
            self.req_nl_after,
        )

    def format_text(self, precede: Text = "", follow: Text = "") -> str:
        add_before = needed_nl_between(precede, self)
        add_after = needed_nl_between(self, follow)

        # return with the required additional newlines
        return "\n" * add_before + self.text + "\n" * add_after
