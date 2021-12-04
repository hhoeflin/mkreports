import functools
from pathlib import Path
from typing import Literal

import mdutils.tools as mdt

from .md_obj import MdObj
from .text import SpacedText


class Header(MdObj):
    def __init__(
        self,
        title: str,
        level: int,
        style: Literal["atx", "setext"] = "atx",
    ) -> None:
        self._title = title
        self._level = level
        self._style = style

    def to_markdown(self, path: Path) -> SpacedText:
        header = mdt.Header.Header.choose_header(
            self._level, self._title, self._style
        ).strip("\n")
        return SpacedText(
            mdt.Header.Header.choose_header(
                self._level, self._title, self._style
            ).strip("\n"),
            (1, 2),
        )


H1 = functools.partial(Header, level=1)
H2 = functools.partial(Header, level=2)
H3 = functools.partial(Header, level=3)
H4 = functools.partial(Header, level=4)
H5 = functools.partial(Header, level=5)
H6 = functools.partial(Header, level=6)
H7 = functools.partial(Header, level=7)
