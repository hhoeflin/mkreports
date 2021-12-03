from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Optional

from .counters import Counters
from .text import ensure_newline

StoreFunc = Callable[[Path, bool, bool], None]


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
        from .list import MdSeq

        first = self if isinstance(self, MdSeq) else MdSeq([self])
        second = other if isinstance(other, MdSeq) else MdSeq([other])

        return first + second

    def __radd__(self, other) -> "MdSeq":
        from .list import MdSeq

        first = other if isinstance(self, MdSeq) else MdSeq([other])
        second = self if isinstance(other, MdSeq) else MdSeq([self])

        return first + second

    def store(self, store_func: Optional[StoreFunc] = None) -> "MdObj":
        """
        Stores assets in a file.

        Some markdown objects (e.g. images, links) may have associated assets
        that need to be stored. This method call with an ingest function
        performs the storing of the file and returns an MdObj that now references
        the stored file.
        """
        return self

    def require_store(self) -> bool:
        """
        Check if the object requires storage.
        """
        return False

    def localize(self, path: Optional[Path] = None) -> "MdObj":
        """
        Make file paths relative to 'path'.

        Markdown documents typically references files relative to itself.
        For objects that reference absolute paths, this method returns
        them relative to 'path'.
        """
        return self

    def require_localize(self) -> bool:
        """
        Does the object require a path to make file stores relative.
        """
        return False

    def count(self, counters: Optional[Counters] = None) -> "MdObj":
        """
        Objects that may need counters, such as references.
        """
        return self

    def require_count(self) -> bool:
        """Does the object require counters."""
        return False

    def backmatter(self) -> str:
        """Return the parts of the object required for the backmatter."""
        return ""

    @abstractmethod
    def to_markdown(self) -> str:
        """
        Convert the object to markdown.

        Assumes that all other processing steps are done, such as storing, localiztion,
        and counting.
        """
        pass

    def to_md_with_bm(self) -> str:
        """
        Convert to markdown and attach the backmatter.
        """
        bm = self.backmatter()

        if bm == "":
            return self.to_markdown()
        else:
            return ensure_newline(self.to_markdown(), 0, 2) + self.backmatter()

    def final_child(self) -> "MdObj":
        """Return the last child, following all children."""
        if self._child is None:
            return self
        else:
            return self._child.final_child()

    def process_all(
        self,
        store_func: Optional[StoreFunc] = None,
        path: Optional[Path] = None,
        counters: Optional[Counters] = None,
    ) -> str:
        return self.store(store_func).localize(path).count(counters).to_md_with_bm()
