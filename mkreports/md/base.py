import copy
from pathlib import Path
from typing import Optional, Union

from .counters import Counters
from .md_obj import MdObj, StoreFunc
from .utils import ensure_newline


class Raw(MdObj):
    """
    Class to encapsulate raw markdown.
    """

    def __init__(self, raw: str):
        super().__init__()
        self.raw = raw

    def to_markdown(self) -> str:
        return self.raw


class MdWrapper(MdObj):
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

    def store(self, store_func: Optional[StoreFunc] = None) -> "MdWrapper":
        if self.require_store():
            self_copy = copy.copy(self)
            self._child = self_copy
            self_copy._obj = self._obj.store(store_func)
            return self_copy
        else:
            return self
        return self._obj.store(store_func)

    def require_store(self) -> bool:
        return self._obj.require_store()

    def localize(self, path: Optional[Path] = None) -> "MdWrapper":
        if self.require_localize():
            self_copy = copy.copy(self)
            self._child = self_copy
            self_copy._obj = self._obj.localize(path)
            return self_copy
        else:
            return self

    def require_localize(self) -> bool:
        return self._obj.require_localize()

    def count(self, counters: Optional[Counters] = None) -> "MdWrapper":
        if self.require_count():
            self_copy = copy.copy(self)
            self._child = self_copy
            self_copy._obj = self._obj.count(counters)
            return self_copy
        else:
            return self

    def require_count(self) -> bool:
        return self._obj.require_count()

    def backmatter(self) -> str:
        return self._obj.backmatter()

    def to_markdown(self) -> str:
        return self._obj.to_markdown()

    def final_child(self) -> "MdObj":
        return self._obj.final_child()


class MdParagraph(MdWrapper):
    def to_markdown(self) -> str:
        return ensure_newline(super().to_markdown(), 1, 2)
