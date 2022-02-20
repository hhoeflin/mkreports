import functools
from dataclasses import dataclass
from typing import Literal, Optional, Union

import mdutils.tools as mdt

from .base import Anchor, MdObj
from .md_proxy import register_md
from .text import SpacedText


@register_md("Heading")
@dataclass
class Heading(MdObj):
    """
    Create a heading.

    Pre-defined heading levels exists as exported objects 'H1' to 'H7'.

    Args:
        title (str): The heading title.
        level (int): Level of the heading.
        style (Literal["atx", "setext"]): Style of the heading in markdown.
        anchor (Optional[Union[Anchor, str]]): Anchor to be added to heading.
    """

    title: str
    level: int
    style: Literal["atx", "setext"] = "atx"
    anchor: Optional[Union[Anchor, str]] = None

    def __post_init__(self):
        if isinstance(self.anchor, str):
            self.anchor = Anchor(self.anchor)

        heading = mdt.Header.Header.choose_header(
            self.level, self.title, self.style
        ).strip("\n")

        if isinstance(self.anchor, Anchor):
            # note, string conversion to Anchor done in post-init
            heading += self.anchor.body.text

        self._body = SpacedText(
            heading,
            (2, 2),
        )

        self._back = None
        self._settings = None


H1 = register_md("H1")(functools.partial(Heading, level=1))
H2 = register_md("H2")(functools.partial(Heading, level=2))
H3 = register_md("H3")(functools.partial(Heading, level=3))
H4 = register_md("H4")(functools.partial(Heading, level=4))
H5 = register_md("H5")(functools.partial(Heading, level=5))
H6 = register_md("H6")(functools.partial(Heading, level=6))
H7 = register_md("H7")(functools.partial(Heading, level=7))
