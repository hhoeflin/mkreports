from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Mapping, Tuple, Union

import yaml
from more_itertools import unique_everseen

from .utils import snake_to_text

NavEntry = Tuple[List[str], Path]
Nav = List[NavEntry]
MkdocsNav = List[Union[str, Mapping[str, Union[str, "MkdocsNav"]]]]


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


def add_nav_entry(mkdocs_settings, nav_entry: NavEntry) -> None:
    mkdocs_settings = deepcopy(mkdocs_settings)
    nav = mkdocs_to_nav(mkdocs_settings["nav"]) + [nav_entry]
    # we need to deduplicate
    nav = list(unique_everseen(nav))
    mkdocs_nav = nav_to_mkdocs(nav)
    mkdocs_settings["nav"] = mkdocs_nav

    return mkdocs_settings


def load_yaml(file: Path) -> Any:
    if file.exists():
        with file.open("r") as f:
            res = yaml.load(f, Loader=yaml.Loader)
    else:
        res = {}

    return res


def save_yaml(obj: Any, file: Path) -> None:
    with file.open("w") as f:
        yaml.dump(obj, f, default_flow_style=False)
