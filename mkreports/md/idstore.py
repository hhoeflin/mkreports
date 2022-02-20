from collections import defaultdict
from copy import copy
from typing import Dict


class IDStore:
    """
    Store for ids. Used to create unique IDs on a page.
    """

    _counts: Dict[str, int]
    _used: set[str]

    def __init__(self, start_with: int = 0, used_ids: set[str] = set()) -> None:
        """
        Initialize the IDStore.

        Args:
            start_with (int): First value of the counter.
            used_ids (set[str]): Set of IDs that have to be avoided as they are
                otherwise used.
        """
        self._count = defaultdict(lambda: start_with - 1)
        self._used = copy(used_ids)
        self._start_with = start_with

    def _increment(self, prefix: str) -> int:
        """
        Returns the next value of the counter (and increments).
        """
        self._count[prefix] += 1
        return self._count[prefix]

    def next_id(self, prefix: str) -> str:
        """
        Returns an id with a counted number at the end.

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
