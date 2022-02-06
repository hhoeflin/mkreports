import functools
import html
import textwrap
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from os.path import relpath
from pathlib import Path
from typing import Any, Dict, Iterable, NamedTuple, Optional, Tuple, Union

from .idstore import IDStore
from .settings import Settings
from .text import SpacedText, Text

store_path_dict = {}


class MdOut(NamedTuple):
    body: SpacedText = SpacedText("")
    back: SpacedText = SpacedText("")


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

    @abstractmethod
    def to_markdown(self, page_path: Path, idstore: IDStore, **kwargs) -> MdOut:
        """
        Convert the object to markdown.

        Assumes that all other processing steps are done, such as storing,
        and counting.
        """
        pass

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

    def to_markdown(self, **kwargs) -> MdOut:
        mdout_list = [x.to_markdown(**kwargs) for x in self.items]
        return MdOut(
            body=functools.reduce(
                lambda x, y: x + y, [elem.body for elem in mdout_list]
            ),
            back=functools.reduce(
                lambda x, y: x + y, [elem.back for elem in mdout_list]
            ),
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

    def to_markdown(self, **kwargs) -> MdOut:
        del kwargs
        return MdOut(body=SpacedText(self.raw))


@dataclass()
class Anchor(MdObj):
    name: str

    def to_markdown(self, **kwargs) -> MdOut:
        del kwargs
        return MdOut(body=SpacedText(f"[](){{:name='{self.name}'}}", (0, 0)))


@dataclass()
class Link(MdObj):
    text: str = ""
    to_page_path: Optional[Path] = None
    anchor: Optional[Union[str, Anchor]] = None
    url: Optional[str] = None

    def to_markdown(self, page_path: Path, **kwargs) -> MdOut:
        del kwargs
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

        return MdOut(body=SpacedText(f"[{html.escape(self.text)}]({link})", (0, 0)))


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

    def to_markdown(self, **kwargs) -> MdOut:
        obj_out = self.obj.to_markdown(**kwargs)
        if isinstance(self.anchor, Anchor):
            # note, string conversion to Anchor done in post-init
            res_body = (
                SpacedText(obj_out.body.text, (0, 1))
                + self.anchor.to_markdown(**kwargs).body
            )
        else:
            res_body = obj_out.body
        return MdOut(body=SpacedText(res_body, (2, 2)), back=obj_out.back)


def comment(x: str) -> SpacedText:
    return SpacedText(f"[comment]: # ({x})", (2, 1))


def comment_ids(id: str) -> SpacedText:
    return comment(f"id: {id}")
