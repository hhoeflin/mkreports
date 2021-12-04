from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .counters import Counters
from .text import SpacedText, Text


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

    def _save(self, child: "MdObj") -> "MdObj":
        # check if child is self
        if id(child) != id(self):
            self._child = child
        return child

    def store(self, store_path: Optional[Path] = None) -> "MdObj":
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

    def count(self, counters: Optional[Counters] = None) -> "MdObj":
        """
        Objects that may need counters, such as references.
        """
        return self

    def require_count(self) -> bool:
        """Does the object require counters."""
        return False

    def backmatter(self, path: Optional[Path]) -> SpacedText:
        """Return the parts of the object required for the backmatter."""
        return SpacedText("")

    @abstractmethod
    def to_markdown(self, path: Optional[Path]) -> SpacedText:
        """
        Convert the object to markdown.

        Assumes that all other processing steps are done, such as storing,
        and counting.
        """
        pass

    def to_md_with_bm(self, path: Optional[Path]) -> SpacedText:
        """
        Convert to markdown and attach the backmatter.
        """
        return SpacedText(self.to_markdown(path), (1, 2)) + SpacedText(
            self.backmatter(path), (2, 1)
        )

    def final_child(self) -> "MdObj":
        """Return the last child, following all children."""
        if self._child is None:
            return self
        else:
            return self._child.final_child()

    def process_all(
        self,
        store_path: Optional[Path] = None,
        path: Optional[Path] = None,
        counters: Optional[Counters] = None,
    ) -> SpacedText:
        return self.store(store_path).count(counters).to_md_with_bm(path)
