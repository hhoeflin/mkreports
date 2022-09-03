"""IDStore object for creating ids in pages."""
from collections import defaultdict
from copy import copy
from functools import partial
from typing import Dict, Set

import attrs


def _identity(x):
    return x


@attrs.mutable(slots=False, init=False)
class IDStore:
    """Store for ids used by a page."""

    _count: Dict[str, int]
    _used: Set[str]
    _start_with: int

    def __init__(self, start_with: int = 0, used_ids: Set[str] = set()) -> None:
        """
        Initialize the IDStore.

        Args:
            start_with (int): First value of the counter.
            used_ids (set[str]): Set of IDs that have to be avoided as they are
                otherwise used.
        """
        IDStore.__attrs_init__(  # type: ignore
            self,
            count=defaultdict(partial(_identity, start_with - 1)),
            used=copy(used_ids),
            start_with=start_with,
        )

    def _increment(self, prefix: str) -> int:
        """Return the next value of the counter (and increment)."""
        self._count[prefix] += 1
        return self._count[prefix]

    def next_id(self, prefix: str) -> str:
        """
        Return an id with a counted number at the end.

        Args:
            prefix (str): Prefix to be used for the ID.

        Returns:
            str: ID as a string.
        """
        # get the next id until it has not been used yet
        while (next_id := f"{prefix}-{self._increment(prefix)}") in self._used:
            pass
        self._used.add(next_id)
        return next_id

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.__dict__ == other.__dict__
