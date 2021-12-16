import functools
from abc import ABC, abstractmethod
from collections.abc import MutableSequence
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Union

from mdutils.tools.TextUtils import TextUtils
from mkreports.settings import Settings

from .text import SpacedText


class MdObj(ABC):
    """
    A class for representing markdown objects.

    Using this class we will be able to compose markdown objects
    in various ways.
    """

    _child: Optional["MdObj"]

    def __init__(self) -> None:
        self._child = None

    def __eq__(self, other) -> bool:
        """
        Check equality of MdObj. Here, _child is ignored.
        """
        if type(self) != type(other):
            return False
        if set(self.__dict__.keys()) != set(other.__dict__.keys()):
            return False
        for key in self.__dict__.keys():
            if key != "_child":
                if self.__dict__["key"] != other.__dict__["key"]:
                    return False
        return True

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


class MdSeq(MdObj, MutableSequence):
    """
    Class to caputre a list of other MdObjs.
    """

    _list: List[MdObj]

    def __init__(self, items: Union[str, Iterable[Union[MdObj, str]]] = ()):
        """
        Create a list of markdown objects.

        All items are appended to list as they are. Strings
        are wrapped as Raw objects.
        """
        super().__init__()
        if isinstance(items, str):
            items = [items]
        self._list = [x if not isinstance(x, str) else Raw(x) for x in items]

    def __getitem__(self, index: int) -> MdObj:
        return self._list[index]

    def __setitem__(self, index: int, value: MdObj) -> None:
        self._list[index] = value

    def __delitem__(self, index: int) -> None:
        del self._list[index]

    def __len__(self) -> int:
        return len(self._list)

    def __add__(self, other) -> "MdSeq":
        second = other if type(other) == MdSeq else MdSeq([other])
        return MdSeq(self._list + second._list)

    def __radd__(self, other) -> "MdSeq":
        second = other if type(other) == MdSeq else MdSeq([other])
        return MdSeq(second._list + self._list)

    def insert(self, index: int, value: MdObj) -> None:
        self._list.insert(index, value)

    def backmatter(self, path: Optional[Path] = None) -> SpacedText:
        return functools.reduce(
            lambda x, y: x + y, [elem.backmatter(path) for elem in self._list]
        )

    def to_markdown(self, path: Optional[Path] = None) -> SpacedText:
        return functools.reduce(
            lambda x, y: x + y, [elem.to_markdown(path) for elem in self._list]
        )

    def req_settings(self) -> Settings:
        """Requirements for the object."""
        # merge the requirements for all individual elements
        res = Settings()
        for elem in self._list:
            res += elem.req_settings()
        return res


class Raw(MdObj):
    """
    Class to encapsulate raw markdown.
    """

    def __init__(self, raw: str):
        super().__init__()
        self.raw = raw

    def to_markdown(self, path: Optional[Path] = None) -> SpacedText:
        return SpacedText(self.raw)


class MdParagraph(MdObj):
    """
    Wraps an object in a paragraph.
    """

    _obj: MdObj

    def __init__(self, obj: Union[str, MdObj]) -> None:
        if isinstance(obj, str):
            obj = Raw(obj)
        self._obj = obj

    def backmatter(self, page_path: Optional[Path] = None) -> SpacedText:
        return self._obj.backmatter(page_path)

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        return SpacedText(self._obj.to_markdown(page_path), (1, 2))


class Code(MdObj):
    """Wrapper class for code."""

    def __init__(
        self,
        code: str,
        title: Optional[str] = None,
        first_line: Optional[int] = None,
        hi_lines: Optional[Tuple[int, int]] = None,
        language: Optional[str] = "python",
    ) -> None:
        self.code = code
        self.title = title
        self.language = language
        self.first_line = first_line
        self.hi_lines = hi_lines

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        annots = ""
        if self.language is not None:
            annots = annots + self.language
        if self.title is not None:
            annots = annots + f' title="{self.title}"'
        if self.first_line is not None:
            # hi_lines get intrepreted relative to first_line
            if self.hi_lines is not None:
                hi_lines = (
                    self.hi_lines[0] - self.first_line + 1,
                    self.hi_lines[1] - self.first_line + 1,
                )
            annots = annots + f' linenums="{self.first_line}"'

        if self.hi_lines is not None:
            annots = annots + f' hl_lines="{self.hi_lines[0]}-{self.hi_lines[1]}"'

        return SpacedText(TextUtils.insert_code(self.code, annots), (2, 2))
