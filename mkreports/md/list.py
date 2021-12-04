import functools
from collections.abc import MutableSequence
from pathlib import Path
from typing import Iterable, List, Optional, Union

from .base import Raw
from .counters import Counters
from .md_obj import MdObj
from .text import SpacedText


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

    def store(self, store_path: Optional[Path]) -> "MdSeq":
        return MdSeq(x.store(store_path) for x in self._list)

    def require_store(self) -> bool:
        return any(x.require_store() for x in self._list)

    def count(self, counters: Counters) -> "MdSeq":
        return MdSeq(x.count(counters) for x in self._list)

    def require_count(self) -> bool:
        return any(x.require_count() for x in self._list)

    def backmatter(self, path: Path) -> SpacedText:
        return functools.reduce(
            lambda x, y: x + y, [elem.backmatter(path) for elem in self._list]
        )

    def to_markdown(self, path: Path) -> SpacedText:
        return functools.reduce(
            lambda x, y: x + y, [elem.to_markdown(path) for elem in self._list]
        )

    def final_child(self) -> "MdSeq":
        return MdSeq(x.final_child() for x in self._list)
