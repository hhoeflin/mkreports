import functools
import html
import textwrap
from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from os.path import relpath
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple, Union

from .md_proxy import register_md
from .settings import PageInfo, Settings
from .text import SpacedText, Text

store_path_dict = {}


class MdObj(ABC):
    """
    A class for representing markdown objects.

    Using this class we will be able to compose markdown objects
    in various ways. It enables adding of objects, which composes
    them sequentially.

    Added them adds the body and back separately as well as merges
    the settings.

    The body is being nested inside other objects as needed. The 'back'
    will always be added without indentation and after adding the body
    (this is useful for e.g. script-tags, but also markdown references).

    The settings will be added at the top of the page or the entire report,
    depending on what was requested.

    End-users should never have to call this class.
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
        """
        Default handler returning the body.

        For subclasses, this can be used by setting 'self._body', but
        can also be overriden.

        Returns:
            SpacedText: A string representing the body with info on how many
                newlines are expected before and after.
        """
        return self._body if self._body is not None else SpacedText("")

    @property
    def back(self) -> SpacedText:
        """
        Default handler returning the backmatter.

        For subclasses, this can be used by setting 'self._back', but
        can also be overriden.

        Returns:
            SpacedText: A string representing the backmatter with info on how many
                newlines are expected before and after.
        """
        return self._back if self._back is not None else SpacedText("")

    @property
    def settings(self) -> Settings:
        """
        Default handler returning the settings.

        For subclasses, this can be used by setting 'self._settings', but
        can also be overriden.

        Returns:
            Settings: A settings object.
        """
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

        Args:
            items (Union[str, Iterable[Union[MdObj, str]]]): A single string can be
                given (which will internally be wrapped as a list of length 1, or
                a list of strings or markdown objects. Strings will be wrapped
                with a 'Raw' object.
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
        """
        Body of the object in markdown - concatenating all individual items.

        Returns:
            SpacedText: The body as a SpacedText object.
        """
        if len(self.items) == 0:
            return SpacedText("")
        else:
            return functools.reduce(
                lambda x, y: x + y, [elem.body for elem in self.items]
            )

    @property
    def back(self) -> SpacedText:
        """
        Back of the object in markdown - concatenating all individual items.

        Returns:
            SpacedText: The back as a SpacedText object.
        """
        if len(self.items) == 0:
            return SpacedText("")
        else:
            return functools.reduce(
                lambda x, y: x + y, [elem.back for elem in self.items]
            )

    @property
    def settings(self) -> Settings:
        """
        Setting to be added to page or report.

        Returns:
            Settings: A settings object.

        """
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
        back: Text = "",
        page_settings=None,
        mkdocs_settings=None,
    ):
        """
        Create the 'Raw' object.

        Args:
            raw (Text): The text to take as is to markdown.
            dedent (): Should the passed text be 'dedented'. Useful for strings
                in triple-quotes that are indented.
            back (): The back to be added. As it has be be left-aligned, will always be
                dedented.
            page_settings (): Settings to be added for the page.
            mkdocs_settings (): Settings for the entire report.
        """
        super().__init__()
        if dedent:
            # we only apply dedent to raw strings
            if isinstance(raw, str):
                raw = textwrap.dedent(raw)
        if isinstance(back, str):
            back = textwrap.dedent(back)

        self._body = SpacedText(raw)
        self._back = SpacedText(back)
        self._settings = Settings(
            page=page_settings if page_settings is not None else {},
            mkdocs=mkdocs_settings if mkdocs_settings is not None else {},
        )


@register_md("Anchor")
class Anchor(MdObj):
    """
    Create an anchor object.

    Args:
        name (str): Name of the anchor.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        prefix: str = "anchor",
        page_info: Optional[PageInfo] = None,
    ):
        if name is None:
            assert page_info is not None
            assert page_info.idstore is not None
            # need to create it using the IDStore
            name = page_info.idstore.next_id(prefix)
            self._back = SpacedText(comment_ids(name), (2, 2))
        else:
            self._back = None

        self.name = name
        self._body = SpacedText(f"[](){{:name='{name}'}}", (0, 0))
        self._settings = None


@register_md("Link")
@dataclass()
class Link(MdObj):
    """
    Create a link to another page.

    Args:
        text (str): The text of the link
        url (Optional[str]): URL to link to.
    """

    text: str = ""
    url: str = ""

    def __post_init__(self):
        link = self.url

        self._body = SpacedText(f"[{html.escape(self.text)}]({link})", (0, 0))
        self._back = None
        self._settings = None


@register_md("ReportLink")
class ReportLink(Link):
    def __init__(
        self,
        text: str = "",
        to_page_path: Optional[Path] = None,
        anchor: Optional[Union[str, Anchor]] = None,
        page_info: Optional[PageInfo] = None,
    ):
        """
        Create a link to another page in this report.

        Args:
            text (str): The text of the link
            page_info (Optional[PageInfo]): PageInfo object cotaining info of the page
            to_page_path (Optional[Path]): internal page to link to
            anchor (Optional[Union[str, Anchor]]): anchor to use
        """
        assert page_info is not None
        assert (page_path := page_info.page_path) is not None
        if to_page_path is None:
            if anchor is None:
                raise ValueError(
                    "Either id or to_page_path and page_path have to be defined"
                )
            else:
                # assume is on the same page
                anchor_id = anchor if isinstance(anchor, str) else anchor.name
                link = f"#{anchor_id}"
        else:
            # both are not none, do relative
            if anchor is None:
                link = f"{relpath(to_page_path, start=page_path.parent)}"
            else:
                anchor_id = anchor if isinstance(anchor, str) else anchor.name
                link = f"{relpath(to_page_path, start=page_path.parent)}#{anchor_id}"
        super().__init__(text=text, url=link)


@register_md("P")
@register_md("Paragraph")
@dataclass
class Paragraph(MdObj):
    """
    Wraps an object in a paragraph.

    Similar to 'Raw', but ensures 2 newlines before and after the text and
    supports adding an anchor to the paragraph.
    """

    obj: MdObj
    anchor: Optional[Union[Anchor, str]]

    def __init__(
        self, obj: Union[str, MdObj], anchor: Optional[Union[Anchor, str]] = None
    ):
        """
        Initialize the paragraph.

        Args:
            obj (Union[str, MdObj]): Markdown object or string. String will be wrapped in
                'Raw'.
            anchor (Optional[Union[Anchor, str]]): Anchor to add to the paragraph.
        """
        self.obj = obj if not isinstance(obj, str) else Raw(obj)
        self.anchor = anchor if not isinstance(anchor, str) else Anchor(anchor)

        if isinstance(self.anchor, Anchor):
            # note, string conversion to Anchor done in post-init
            res_body = SpacedText(self.obj.body.text, (0, 1)) + self.anchor.body
        else:
            res_body = self.obj.body
        self._body = SpacedText(res_body, (2, 2))
        self._back = None if not isinstance(self.anchor, Anchor) else self.anchor.back
        self._settings = None


def comment(x: str) -> SpacedText:
    """
    Create a comment for markdown.

    Args:
        x (str): The string to put into the comment.

    Returns:
        SpacedText: The comment line to be added as backmatter.

    """
    return SpacedText(f"[comment]: # ({x})", (2, 1))


def comment_ids(id: str) -> SpacedText:
    """
    Put an id into a comment.

    Args:
        id (str): The ID to insert.

    Returns:
        SpacedText: The comment-id to be added as backmatter.

    """
    return comment(f"id: {id}")
