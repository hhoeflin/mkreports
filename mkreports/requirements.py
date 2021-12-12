from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Tuple, Union

import yaml
from deepmerge import Merger

NavEntry = Tuple[List[str], Path]
Nav = List[NavEntry]
MkdocsNav = List[Union[str, Mapping[str, Union[str, "MkdocsNav"]]]]


def true_stem(path: Path) -> str:
    """True stem of a path, without all suffixes, not just last."""
    return path.name[: -(len("".join(path.suffixes)))]


def snake_to_text(x: str) -> str:
    """Convert snake case to regular text, with each word capitalized."""
    return " ".join([w.capitalize() for w in x.split("_")])


def path_to_nav_entry(path: Path) -> NavEntry:
    return (
        [snake_to_text(x) for x in path.parent.parts] + [snake_to_text(path.stem)],
        path,
    )


def check_length_one(
    x: Mapping[str, Union[str, "MkdocsNav"]]
) -> Tuple[str, Union[str, MkdocsNav]]:
    assert len(x) == 1
    return list(x.items())[0]


def mkdocs_to_nav(mkdocs_nav: MkdocsNav) -> Nav:
    """
    Convert an mkdovs nav to a list of NavEntry.
    """
    res = []
    for entry in mkdocs_nav:
        if isinstance(entry, str):
            res.append(([], Path(entry)))
        elif isinstance(entry, Mapping):
            key, val = check_length_one(entry)
            if isinstance(val, str):
                res.append(([key], Path(val)))
            elif isinstance(val, List):
                res = res + [([key] + h, p) for (h, p) in mkdocs_to_nav(val)]
            else:
                raise Exception("Not expected type")
        else:
            raise Exception("Not expected type")
    return res


def split_nav(x: Nav) -> Tuple[List[str], Dict[str, Nav]]:
    res_nav = defaultdict(list)
    res_list = []
    for (h, p) in x:
        if len(h) == 0:
            res_list.append(p)
        else:
            res_nav[h[0]].append((h[1:], p))

    return (res_list, res_nav)


def nav_to_mkdocs(nav: Nav) -> MkdocsNav:
    """
    Convert a list of nav-entries into mkdocs format.
    """
    split_nokey, split_keys = split_nav(nav)
    res: MkdocsNav = [str(p) for p in split_nokey]

    for key, val in split_keys.items():
        mkdocs_for_key = nav_to_mkdocs(val)
        # if it is a list of length 1 with a string, treat it special
        if len(mkdocs_for_key) == 1 and isinstance(mkdocs_for_key[0], str):
            res.append({key: mkdocs_for_key[0]})
        else:
            res.append({key: mkdocs_for_key})

    return res


def strategy_append_new(config, path, base, nxt):
    """prepend nxt to base."""
    return base + [x for x in nxt if x not in base]


req_merger = Merger(
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


@dataclass
class Requirements:
    mkdocs: Dict[str, Any] = field(default_factory=dict)
    mkreports: Dict[str, Any] = field(default_factory=dict)

    def __add__(self, other: "Requirements"):
        """
        Merges mkdocs and mkreports.

        For mkdocs, nav will never be merged and an error thrown if attempted.
        """
        if "nav" in self.mkdocs and "nav" in other.mkdocs:
            raise ValueError(
                "Merging of Requirements with 'nav' in mkdocs not supported."
            )
        return Requirements(
            mkdocs=req_merger.merge(deepcopy(self.mkdocs), deepcopy(other.mkdocs)),
            mkreports=req_merger.merge(
                deepcopy(self.mkreports), deepcopy(other.mkreports)
            ),
        )

    def add_nav_entry(self, nav_entry: NavEntry) -> None:
        nav = mkdocs_to_nav(self.mkdocs["nav"]) + [nav_entry]
        mkdocs_nav = nav_to_mkdocs(nav)
        self.mkdocs["nav"] = mkdocs_nav

    @classmethod
    def load(cls, report_dir: Path) -> "Requirements":
        """
        Load the settings from the mkdocs.yaml and mkreports.yaml.
        """
        mkdocs_file = report_dir / "mkdocs.yaml"
        mkreports_file = report_dir / "mkreports.yaml"
        if mkdocs_file.exists():
            with mkdocs_file.open("r") as f:
                mkdocs_settings = yaml.load(f, Loader=yaml.Loader)
        else:
            mkdocs_settings = {}
        if mkreports_file.exists():
            with (report_dir / "mkreports.yaml").open("r") as f:
                mkreports_settings = yaml.load(f, Loader=yaml.Loader)
        else:
            mkreports_settings = {}

        return Requirements(mkdocs=mkdocs_settings, mkreports=mkreports_settings)

    def save(self, report_dir: Path):
        """
        Save the requirements to the mkdocs.yaml and mkreports.yaml file.
        """
        mkdocs_file = report_dir / "mkdocs.yaml"
        mkreports_file = report_dir / "mkreports.yaml"
        with mkdocs_file.open("w") as f:
            yaml.dump(self.mkdocs, f, default_flow_style=False)
        with mkreports_file.open("w") as f:
            yaml.dump(self.mkreports, f, default_flow_style=False)
