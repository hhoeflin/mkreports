import functools
import html
import textwrap
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from os.path import relpath
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple, Union

from mkreports.settings import Settings

from .text import SpacedText, Text

store_path_dict = {}


class MdObj(ABC):
    """
    A class for representing markdown objects.

    Using this class we will be able to compose markdown objects
    in various ways.
    """

    def __add__(self, other) -> "MdSeq":
        first = self if isinstance(self, MdSeq) else MdSeq([self])
        second = other if isinstance(other, MdSeq) else MdSeq([other])

        return first + second

    def __radd__(self, other) -> "MdSeq":
        first = other if isinstance(self, MdSeq) else MdSeq([other])
        second = self if isinstance(other, MdSeq) else MdSeq([self])

        return first + second

    def backmatter(self, page_path: Optional[Path]) -> SpacedText:
        """Return the parts of the object required for the backmatter."""
        return SpacedText("")

    @abstractmethod
    def to_markdown(self, page_path: Optional[Path]) -> SpacedText:
        """
        Convert the object to markdown.

        Assumes that all other processing steps are done, such as storing,
        and counting.
        """
        pass

    def to_md_with_bm(self, page_path: Optional[Path]) -> SpacedText:
        """
        Convert to markdown and attach the backmatter.
        """
        backmatter = self.backmatter(page_path)
        if backmatter.text == "":
            return self.to_markdown(page_path)
        else:
            return SpacedText(self.to_markdown(page_path), (1, 2)) + SpacedText(
                self.backmatter(page_path), (2, 1)
            )

    def req_settings(self) -> Settings:
        return Settings()


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

    def backmatter(self, path: Optional[Path] = None) -> SpacedText:
        return functools.reduce(
            lambda x, y: x + y, [elem.backmatter(path) for elem in self.items]
        )

    def to_markdown(self, path: Optional[Path] = None) -> SpacedText:
        return functools.reduce(
            lambda x, y: x + y, [elem.to_markdown(path) for elem in self.items]
        )

    def req_settings(self) -> Settings:
        """Requirements for the object."""
        # merge the requirements for all individual elements
        res = Settings()
        for elem in self.items:
            res += elem.req_settings()
        return res


@dataclass()
class Raw(MdObj):
    """
    Class to encapsulate raw markdown.
    """

    raw: Text
    page_settings: Dict[str, Any]
    mkdocs_settings: Dict[str, Any]

    def __init__(
        self, raw: Text = "", dedent=True, page_settings=None, mkdocs_settings=None
    ):
        super().__init__()
        if dedent:
            # we only apply dedent to raw strings
            if isinstance(raw, str):
                raw = textwrap.dedent(raw)

        self.raw = raw
        self.page_settings = page_settings
        self.mkdocs_settings = mkdocs_settings

    def req_settings(self) -> Settings:
        return Settings(
            page=self.page_settings if self.page_settings is not None else {},
            mkdocs=self.mkdocs_settings if self.mkdocs_settings is not None else {},
        )

    def to_markdown(self, path: Optional[Path] = None) -> SpacedText:
        return SpacedText(self.raw)


@dataclass()
class Anchor(MdObj):
    name: str

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        return SpacedText(f"[](){{:name='{self.name}'}}", (0, 0))


@dataclass()
class Link(MdObj):
    text: str = ""
    to_page_path: Optional[Path] = None
    anchor: Optional[Union[str, Anchor]] = None
    url: Optional[str] = None

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        if self.url is not None:
            link = self.url
        else:
            if page_path is None or self.to_page_path is None:
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
                    link = f"{relpath(self.to_page_path, start=page_path.parent)}"
                else:
                    anchor_id = (
                        self.anchor
                        if isinstance(self.anchor, str)
                        else self.anchor.name
                    )
                    link = f"{relpath(self.to_page_path, start=page_path.parent)}#{anchor_id}"

        return SpacedText(f"[{html.escape(self.text)}]({link})", (0, 0))


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

    def backmatter(self, page_path: Optional[Path] = None) -> SpacedText:
        return self.obj.backmatter(page_path)

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        p_text = self.obj.to_markdown(page_path)
        if isinstance(self.anchor, Anchor):
            # note, string conversion to Anchor done in post-init
            p_text = SpacedText(p_text.text, (0, 1)) + self.anchor.to_markdown(
                page_path
            )
        return SpacedText(p_text, (2, 2))
