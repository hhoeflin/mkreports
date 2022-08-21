import functools
from typing import Literal, Optional, Set, Union

import attrs
import mdutils.tools as mdt

from .base import Anchor, MdObj, NamedAnchor, RenderedMd
from .md_proxy import register_md
from .settings import Settings
from .text import SpacedText


@register_md("Heading")
@attrs.mutable()
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
            self.anchor = NamedAnchor(self.anchor)

    def _render(self, **kwargs) -> RenderedMd:

        heading = mdt.Header.Header.choose_header(
            self.level, self.title, self.style
        ).strip("\n")

        if isinstance(self.anchor, Anchor):
            anchor_rendered = self.anchor.render(**kwargs)
            heading += anchor_rendered.body.text
            back = anchor_rendered.back
        else:
            back = SpacedText("")

        body = SpacedText(
            heading,
            (2, 2),
        )

        settings = Settings()
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        if isinstance(self.anchor, Anchor):
            return self.anchor.render_fixtures()
        else:
            return set()


H1 = register_md("H1")(functools.partial(Heading, level=1))
H2 = register_md("H2")(functools.partial(Heading, level=2))
H3 = register_md("H3")(functools.partial(Heading, level=3))
H4 = register_md("H4")(functools.partial(Heading, level=4))
H5 = register_md("H5")(functools.partial(Heading, level=5))
H6 = register_md("H6")(functools.partial(Heading, level=6))
H7 = register_md("H7")(functools.partial(Heading, level=7))
