import functools
import html
import textwrap
from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from os.path import relpath
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple, Union

from mkreports.md_proxy import register_md

from .settings import Settings
from .text import SpacedText, Text

store_path_dict = {}


class MdObj(ABC):
    """
    A class for representing markdown objects.

    Using this class we will be able to compose markdown objects
    in various ways.
    """

    _body: Optional[SpacedText]
    _back: Optional[SpacedText]
    _settings: Optional[Settings]

    def __add__(self, other) -> "MdSeq":
        first = self if isinstance(self, MdSeq) else MdSeq([self])
        second = other if isinstance(other, MdSeq) else MdSeq([other])

        return first + second

    def __radd__(self, other) -> "MdSeq":
        first = other if isinstance(self, MdSeq) else MdSeq([other])
        second = self if isinstance(other, MdSeq) else MdSeq([self])

        return first + second

    @property
    def body(self) -> SpacedText:
        return self._body if self._body is not None else SpacedText("")

    @property
    def back(self) -> SpacedText:
        return self._back if self._back is not None else SpacedText("")

    @property
    def settings(self) -> Settings:
        return self._settings if self._settings is not None else Settings()


@register_md("MdSeq")
class MdSeq(MdObj, Sequence):
    """
    Class to caputre a list of other MdObjs.
    """

    items: Tuple[MdObj, ...]

    def __init__(self, items: Union[str, Iterable[Union[MdObj, str]]] = ()):
        """
        Create a list of markdown objects.

        All items are appended to list as they are. Strings
        are wrapped as Raw objects.
        """
        super().__init__()
        if isinstance(items, str):
            items = [items]
        self.items = tuple([x if not isinstance(x, str) else Raw(x) for x in items])

    def __getitem__(self, index: int) -> MdObj:
        return self.items[index]

    def __len__(self) -> int:
        return len(self.items)

    def __add__(self, other) -> "MdSeq":
        second_items = other.items if type(other) == MdSeq else (other,)
        return MdSeq(self.items + second_items)

    def __radd__(self, other) -> "MdSeq":
        second_items = other if type(other) == MdSeq else (other,)
        return MdSeq(second_items + self.items)

    @property
    def body(self) -> SpacedText:
        if len(self.items) == 0:
            return SpacedText("")
        else:
            return functools.reduce(
                lambda x, y: x + y, [elem.body for elem in self.items]
            )

    @property
    def back(self) -> SpacedText:
        if len(self.items) == 0:
            return SpacedText("")
        else:
            return functools.reduce(
                lambda x, y: x + y, [elem.back for elem in self.items]
            )

    @property
    def settings(self) -> Settings:
        if len(self.items) == 0:
            return Settings()
        else:
            return functools.reduce(
                lambda x, y: x + y, [elem.settings for elem in self.items]
            )


@register_md("Raw")
@dataclass()
class Raw(MdObj):
    """
    Class to encapsulate raw markdown.
    """

    raw: Text
    page_settings: Dict[str, Any]
    mkdocs_settings: Dict[str, Any]

    def __init__(
        self,
        raw: Text = "",
        dedent=True,
        back="",
        page_settings=None,
        mkdocs_settings=None,
    ):
        super().__init__()
        if dedent:
            # we only apply dedent to raw strings
            if isinstance(raw, str):
                raw = textwrap.dedent(raw)

        self._body = SpacedText(raw)
        self._back = SpacedText(back)
        self._settings = Settings(
            page=page_settings if page_settings is not None else {},
            mkdocs=mkdocs_settings if mkdocs_settings is not None else {},
        )


@register_md("Anchor")
@dataclass()
class Anchor(MdObj):
    name: str

    def __post_init__(self):
        self._body = SpacedText(f"[](){{:name='{self.name}'}}", (0, 0))
        self._back = None
        self._settings = None


@register_md("Link")
@dataclass()
class Link(MdObj):
    text: str = ""
    page_path: Optional[Path] = None
    to_page_path: Optional[Path] = None
    anchor: Optional[Union[str, Anchor]] = None
    url: Optional[str] = None

    def __post_init__(self):
        if self.url is not None:
            link = self.url
        else:
            if self.page_path is None or self.to_page_path is None:
                if self.anchor is None:
                    raise ValueError(
                        "Either id or to_page_path and page_path have to be defined"
                    )
                else:
                    # assume is on the same page
                    anchor_id = (
                        self.anchor
                        if isinstance(self.anchor, str)
                        else self.anchor.name
                    )
                    link = f"#{anchor_id}"
            else:
                # both are not none, do relative
                if self.anchor is None:
                    link = f"{relpath(self.to_page_path, start=self.page_path.parent)}"
                else:
                    anchor_id = (
                        self.anchor
                        if isinstance(self.anchor, str)
                        else self.anchor.name
                    )
                    link = f"{relpath(self.to_page_path, start=self.page_path.parent)}#{anchor_id}"

        self._body = SpacedText(f"[{html.escape(self.text)}]({link})", (0, 0))
        self._back = None
        self._settings = None


@register_md("P")
@register_md("Paragraph")
@dataclass
class Paragraph(MdObj):
    """
    Wraps an object in a paragraph.
    """

    obj: MdObj
    anchor: Optional[Union[Anchor, str]]

    def __init__(
        self, obj: Union[str, MdObj], anchor: Optional[Union[Anchor, str]] = None
    ):
        self.obj = obj if not isinstance(obj, str) else Raw(obj)
        self.anchor = anchor if not isinstance(anchor, str) else Anchor(anchor)

        if isinstance(self.anchor, Anchor):
            # note, string conversion to Anchor done in post-init
            self._body = SpacedText(self.obj.body.text, (0, 1)) + self.anchor.body
        else:
            self._body = self.obj.body
        self._back = None
        self._settings = None


def comment(x: str) -> SpacedText:
    return SpacedText(f"[comment]: # ({x})", (2, 1))


def comment_ids(id: str) -> SpacedText:
    return comment(f"id: {id}")
