from typing import Dict


class Counters:
    _counts: Dict[str, int]

    def __init__(self, start_with: int = 0) -> None:
        self._counts = {}
        self._start_with = start_with

    def count(self, name: str) -> int:
        """
        Returns the next value of the counter (and increments).
        """
        if name in self._counts:
            self._counts[name] += 1
        else:
            self._counts[name] = self._start_with
        return self._counts[name]

    def counted_id(self, prefix: str, omit_1: bool = False) -> str:
        """
        Returns an id with a counted number at the end.
        """
        prefix_count = self.count(prefix)
        if omit_1 and prefix_count == 1:
            return prefix
        else:
            return f"{prefix}_{self.count(prefix)}"
