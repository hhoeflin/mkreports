from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict

from deepmerge import Merger


@dataclass
class Settings:
    mkdocs: Dict[str, Any] = field(default_factory=dict)
    page: Dict[str, Any] = field(default_factory=dict)

    def __add__(self, other: "Settings"):
        """
        Merges mkdocs and mkreports.

        For mkdocs, nav will never be merged and an error thrown if attempted.
        """
        if "nav" in self.mkdocs and "nav" in other.mkdocs:
            raise ValueError(
                "Merging of Requirements with 'nav' in mkdocs not supported."
            )
        return Settings(
            mkdocs=merge_settings(self.mkdocs, other.mkdocs),
            page=merge_settings(self.page, other.page),
        )


def strategy_append_new(config, path, base, nxt):
    """prepend nxt to base."""
    del config, path
    return base + [x for x in nxt if x not in base]


settings_merger = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [(list, [strategy_append_new]), (dict, ["merge"]), (set, ["union"])],
    # next, choose the fallback strategies,
    # applied to all other types:
    ["override"],
    # finally, choose the strategies in
    # the case where the types conflict:
    ["override"],
)


def merge_settings(a, b):
    return settings_merger.merge(deepcopy(a), deepcopy(b))
