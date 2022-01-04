import functools
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Union

import mdutils.tools as mdt

from .base import Anchor, MdObj
from .text import SpacedText


@dataclass
class Heading(MdObj):
    title: str
    level: int
    style: Literal["atx", "setext"] = "atx"
    anchor: Optional[Union[Anchor, str]] = None

    def __post_init__(self):
        if isinstance(self.anchor, str):
            self.anchor = Anchor(self.anchor)

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        heading = mdt.Header.Header.choose_header(
            self.level, self.title, self.style
        ).strip("\n")

        if isinstance(self.anchor, Anchor):
            # note, string conversion to Anchor done in post-init
            heading += self.anchor.to_markdown(page_path).text

        return SpacedText(
            heading,
            (2, 2),
        )


H1 = functools.partial(Heading, level=1)
H2 = functools.partial(Heading, level=2)
H3 = functools.partial(Heading, level=3)
H4 = functools.partial(Heading, level=4)
H5 = functools.partial(Heading, level=5)
H6 = functools.partial(Heading, level=6)
H7 = functools.partial(Heading, level=7)
