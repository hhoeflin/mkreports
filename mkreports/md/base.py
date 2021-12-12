import functools
from abc import ABC, abstractmethod
from collections.abc import MutableSequence
from pathlib import Path
from typing import Iterable, List, Optional, Union

from mkreports.requirements import Requirements

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

    def requirements(self) -> Requirements:
        return Requirements()


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

    def requirements(self) -> Requirements:
        """Requirements for the object."""
        # merge the requirements for all individual elements
        res = Requirements()
        for elem in self._list:
            res += elem.requirements()
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
    Wrapper class for an object.

    Passes along all calls to the object being wrapped. This is
    used as a base class for other classes that wrap objects.
    All methods are overwritten except for `to_md_with_bm` and `process_all`.
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
