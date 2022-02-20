from typing import Any, Tuple, Union

Text = Union[str, "SpacedText"]


def count_newlines(x: str, before=True) -> int:
    """
    Count the number of newlines from front or back.

    Here all newlines are counted while ignoring whitespace.
    Stop at first character that is not newline or whitespace.
    If there are no non-newline or whitespace characters, return
    infinite number of newlines.
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


class SpacedText:
    """Representation of text with newlines before or after."""

    text: str
    req_nl: Tuple[int, int]

    def __init__(self, text: Text = "", req_nl: Tuple[int, int] = (0, 0)) -> None:
        """
        Initialize the object.

        Args:
            text (Text): The text to print.
            req_nl (Tuple[int, int]): Number of newlines before and after to ensure.
        """
        if isinstance(text, str):
            my_text = text
            my_req_nl = req_nl
        else:
            my_text = text.text
            my_req_nl = (
                max(req_nl[0], text.req_nl[0]),
                max(req_nl[1], text.req_nl[1]),
            )

        self.text = my_text
        self.req_nl = my_req_nl

    def __str__(self) -> str:
        """
        Return a formatted str.

        We assume that 3 newlines are before and after. That should be enough.
        """
        return self.format_text("\n\n\n", "\n\n\n")

    def __eq__(self, other: Any) -> bool:
        if type(self) != type(other):
            return False
        return self.text == other.text and self.req_nl == other.req_nl

    def __add__(self, follow: Text) -> "SpacedText":
        return _add_text(self, SpacedText(follow))

    def __radd__(self, precede: Text) -> "SpacedText":
        return _add_text(SpacedText(precede), self)

    def format_text(self, precede: Text = "", follow: Text = "") -> str:
        add_before = _needed_nl_between(SpacedText(precede), self)
        add_after = _needed_nl_between(self, SpacedText(follow))

        # return with the required additional newlines
        return ("\n" * add_before) + self.text + ("\n" * add_after)


def _needed_nl_between(first: SpacedText, second: SpacedText) -> int:
    """
    Calculates the number of newlines needed between two text objects.
    """
    if first.text == "" or second.text == "":
        return 0

    req_first_after = first.req_nl[1]
    num_first_after = count_newlines(first.text, before=False)

    req_second_before = second.req_nl[0]
    num_second_before = count_newlines(second.text, before=True)

    add_between = max(
        max(req_first_after, req_second_before) - num_second_before - num_first_after,
        0,
    )
    return add_between


def _add_text(first: SpacedText, second: SpacedText) -> SpacedText:
    # this takes care of empty strings
    add_nl = _needed_nl_between(first, second)

    # if one of the strings is emtpy, we still need to take care of the rest
    ## required is maximum of both on side with ''
    if first.text == "":
        req_before = max(first.req_nl[0], second.req_nl[0])
    else:
        req_before = first.req_nl[0]
    if second.text == "":
        req_after = max(first.req_nl[1], second.req_nl[1])
    else:
        req_after = second.req_nl[1]
    return SpacedText(
        first.text + "\n" * add_nl + second.text,
        (req_before, req_after),
    )
