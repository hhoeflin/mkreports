import functools
import html
import inspect
import textwrap
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from os.path import relpath
from pathlib import Path
from typing import (Any, Callable, Dict, Iterable, Optional, Set, Tuple, Union,
                    final)

import attrs

from .idstore import IDStore
from .md_proxy import register_md
from .settings import Settings
from .text import SpacedText, Text

store_path_dict = {}


class NotRenderedError(Exception):
    pass


def to_spaced_text(x: Union[str, SpacedText, None]) -> SpacedText:
    if isinstance(x, str):
        return SpacedText(x)
    elif x is None:
        return SpacedText("")
    else:
        return x


def to_settings(x: Optional[Settings]) -> Settings:
    if x is None:
        return Settings()
    else:
        return x


@attrs.mutable()
class RenderedMd:
    body: SpacedText
    back: SpacedText
    settings: Settings
    src: "MdObj"

    def __init__(
        self,
        body: Union[str, SpacedText, None],
        back: Union[str, SpacedText, None],
        settings: Optional[Settings],
        src: "MdObj",
    ):
        self.__attrs_init__(  # type: ignore
            body=to_spaced_text(body),
            back=to_spaced_text(back),
            settings=to_settings(settings),
            src=src,
        )


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

    def __add__(self, other) -> "MdSeq":
        first = self if isinstance(self, MdSeq) else MdSeq([self])
        second = other if isinstance(other, MdSeq) else MdSeq([other])

        return first + second

    def __radd__(self, other) -> "MdSeq":
        first = other if isinstance(other, MdSeq) else MdSeq([other])
        second = self if isinstance(self, MdSeq) else MdSeq([self])

        return first + second

    @abstractmethod
    def _render(self) -> RenderedMd:
        pass

    @final
    def render(self, **kwargs) -> RenderedMd:
        used_fixtures = {key: kwargs[key] for key in self.render_fixtures()}
        return self._render(**used_fixtures)

    @abstractmethod
    def render_fixtures(self) -> Set[str]:
        """
        Get the fixtures used by render.

        Returns:
            Set of strings representing the used fixtures.

        """
        pass


def func_kwargs_as_set(f: Callable) -> Set[str]:
    render_sig = inspect.signature(f)
    return set(render_sig.parameters.keys())


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

    def _render(self, **kwargs) -> RenderedMd:
        rendered_items = [item.render(**kwargs) for item in self.items]

        if len(self.items) == 0:
            return RenderedMd(
                body=SpacedText(""), back=SpacedText(""), settings=Settings(), src=self
            )
        else:
            body = functools.reduce(
                lambda x, y: x + y, [elem.body for elem in rendered_items]
            )
            back = functools.reduce(
                lambda x, y: x + y, [elem.back for elem in rendered_items]
            )
            settings = functools.reduce(
                lambda x, y: x + y, [elem.settings for elem in rendered_items]
            )
            return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        # we iterate through all items and concatenate the sets
        fixtures = set()
        for item in self.items:
            fixtures.update(item.render_fixtures())

        return fixtures


@register_md("Raw")
@attrs.mutable()
class Raw(MdObj):
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

    raw: Text = ""
    back: Text = ""
    dedent: bool = True
    page_settings: Dict[str, Any] = attrs.field(factory=dict)
    mkdocs_settings: Dict[str, Any] = attrs.field(factory=dict)

    def __attrs_post_init__(self):
        if self.dedent:
            # we only apply dedent to raw strings
            if isinstance(self.raw, str):
                self.raw = textwrap.dedent(self.raw)
        if isinstance(self.back, str):
            self.back = textwrap.dedent(self.back)

    def _render(self) -> RenderedMd:
        body = SpacedText(self.raw)
        back = SpacedText(self.back)
        settings = Settings(
            page=self.page_settings,
            mkdocs=self.mkdocs_settings,
        )
        return RenderedMd(back=back, body=body, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return set()


@register_md("Anchor")
class Anchor(MdObj):
    name: str

    def __new__(cls, name: Optional[str] = None):
        if name is not None:
            cls = NamedAnchor
            self = object.__new__(cls)
            self.__init__(name=name)
            return self
        else:
            cls = AutoAnchor
            self = object.__new__(cls)
            self.__init__()
            return self


@register_md("NamedAnchor")
class NamedAnchor(Anchor):
    """
    Create an anchor object.

    Args:
        name (str): Name of the anchor.
    """

    def __init__(
        self,
        name: str,
    ):
        self.name = name

    def _render(self) -> RenderedMd:
        back = SpacedText("")

        body = SpacedText(f"[](){{:name='{self.name}'}}", (0, 0))
        settings = Settings()
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return set()


@register_md("AutoAnchor")
class AutoAnchor(Anchor):
    """
    Create an anchor object.

    Args:
        name (str): Name of the anchor.
    """

    def __init__(
        self,
        prefix: str = "anchor",
    ):
        self.prefix = prefix

    def _render(self, idstore: IDStore) -> RenderedMd:
        self.name = idstore.next_id(self.prefix)
        back = SpacedText(comment_ids(self.name), (2, 2))
        body = SpacedText(f"[](){{:name='{self.name}'}}", (0, 0))
        settings = Settings()
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return func_kwargs_as_set(self._render)


@register_md("Link")
@attrs.mutable()
class Link(MdObj):
    """
    Create a link to another page.

    Args:
        text (str): The text of the link
        url (Optional[str]): URL to link to.
    """

    text: str = ""
    url: str = ""

    def _render(self) -> RenderedMd:
        body = SpacedText(f"[{html.escape(self.text)}]({self.url})", (0, 0))
        back = SpacedText("")
        settings = Settings()
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return set()


@register_md("ReportLink")
class ReportLink(Link):
    def __init__(
        self,
        text: str = "",
        to_page_path: Optional[Union[str, Path]] = None,
        anchor: Optional[Union[str, Anchor]] = None,
    ):
        """
        Create a link to another page in this report.

        Args:
            text (str): The text of the link
            to_page_path (Optional[Path]): internal page to link to
            anchor (Optional[Union[str, Anchor]]): anchor to use
        """
        if isinstance(anchor, str):
            self.anchor = NamedAnchor(anchor)
        else:
            self.anchor = anchor
        self.to_page_path = (
            Path(to_page_path) if isinstance(to_page_path, str) else to_page_path
        )
        self.text = text

    def _render(self, page_path: Path) -> RenderedMd:

        if self.to_page_path is None:
            if self.anchor is None:
                raise ValueError(
                    "Either id or to_page_path and page_path have to be defined"
                )
            else:
                # assume is on the same page
                link = f"#{self.anchor.name}"
        else:
            # both are not none, do relative
            if self.anchor is None:
                link = f"{relpath(self.to_page_path, start=page_path.parent)}"
            else:
                link = f"{relpath(self.to_page_path, start=page_path.parent)}#{self.anchor.name}"
        self.url = link
        return super()._render()

    def render_fixtures(self) -> Set[str]:
        return func_kwargs_as_set(self._render)


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
        self.anchor = anchor if not isinstance(anchor, str) else NamedAnchor(anchor)

    def _render(self, **kwargs) -> RenderedMd:
        obj_rendered = self.obj.render(**kwargs)
        if isinstance(self.anchor, Anchor):
            anchor_rendered = self.anchor.render(**kwargs)
            # note, string conversion to Anchor done in post-init
            body = SpacedText(obj_rendered.body.text, (0, 1)) + anchor_rendered.body
            back = obj_rendered.back + anchor_rendered.back
        else:
            body = obj_rendered.body
            back = obj_rendered.back
        body = SpacedText(body, (2, 2))
        settings = Settings()

        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        fixtures = self.obj.render_fixtures()
        if isinstance(self.anchor, Anchor):
            fixtures.update(self.anchor.render_fixtures())
        return fixtures


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
