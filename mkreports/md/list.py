from collections.abc import MutableSequence
from pathlib import Path
from typing import Iterable, List, Optional, Union

from .base import Raw
from .counters import Counters
from .md_obj import MdObj, StoreFunc
from .utils import ensure_newline


class MdList(MdObj, MutableSequence):
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

    def __add__(self, other) -> "MdList":
        second = other if type(other) == MdList else MdList([other])
        return MdList(self._list + second._list)

    def __radd__(self, other) -> "MdList":
        second = other if type(other) == MdList else MdList([other])
        return MdList(second._list + self._list)

    def insert(self, index: int, value: MdObj) -> None:
        self._list.insert(index, value)

    def store(self, store_func: Optional[StoreFunc]) -> "MdList":
        return MdList(x.store(store_func) for x in self._list)

    def require_store(self) -> bool:
        return any(x.require_store() for x in self._list)

    def localize(self, path: Optional[Path]) -> "MdList":
        return MdList(x.localize(path) for x in self._list)

    def require_localize(self) -> bool:
        return any(x.require_localize() for x in self._list)

    def count(self, counters: Counters) -> "MdList":
        return MdList(x.count(counters) for x in self._list)

    def require_count(self) -> bool:
        return any(x.require_count() for x in self._list)

    def backmatter(self) -> str:
        return "".join([x.backmatter() for x in self._list])

    def to_markdown(self) -> str:
        return "".join([x.to_markdown() for x in self._list])

    def final_child(self) -> "MdList":
        return MdList(x.final_child() for x in self._list)
