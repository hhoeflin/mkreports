from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Mapping, NamedTuple, Sequence, Tuple, Union

import yaml
from more_itertools import unique_everseen

from .utils import snake_to_text


class NavEntry(NamedTuple):
    """
    An entry in the navigation tab.

    Args:
        hierarchy (Sequence[str]): List of navigation entries.
        file (Path): Path to the page, relative to report docs folder.
    """

    hierarchy: Sequence[str]
    rel_path: Path


Nav = List[NavEntry]
MkdocsNav = List[Union[str, Mapping[str, Union[str, "MkdocsNav"]]]]


def path_to_nav_entry(path: Path) -> NavEntry:
    """
    Turn a file path into a NavEntry.

    The path is split, each part of the path used as an element of the
    hierarchy. Snake-case are split into words with first letters
    capitalized.

    Args:
        path (Path): The path relative to the report docs folder to turn
            into a nav-entry.

    Returns:
        NavEntry: The NavEntry object representing the path and
            the hierarchy of navigation entries.

    """
    return NavEntry(
        tuple(
            [snake_to_text(x) for x in path.parent.parts] + [snake_to_text(path.stem)]
        ),
        path,
    )


def _check_length_one(
    x: Mapping[str, Union[str, "MkdocsNav"]]
) -> Tuple[str, Union[str, MkdocsNav]]:
    assert len(x) == 1
    return list(x.items())[0]


def mkdocs_to_nav(mkdocs_nav: MkdocsNav) -> Nav:
    """
    Convert an mkdocs nav to a list of NavEntry.

    Args:
        mkdocs_nav: A python representation of the nav-entry
            in the mkdocs.yml file.
    """
    res = []
    for entry in mkdocs_nav:
        if isinstance(entry, str):
            res.append(NavEntry([], Path(entry)))
        elif isinstance(entry, Mapping):
            key, val = _check_length_one(entry)
            if isinstance(val, str):
                res.append(NavEntry([key], Path(val)))
            elif isinstance(val, List):
                res = res + [
                    NavEntry((key,) + tuple(h), p) for (h, p) in mkdocs_to_nav(val)
                ]
            else:
                raise Exception("Not expected type")
        else:
            raise Exception("Not expected type")
    return res


def split_nav(x: Nav) -> Tuple[List[str], Dict[str, Nav]]:
    """
    Split the navigation entry into top level list of items and dict of Navs.

    Given a nav-entry, each top-level item that is not a hierarchy itself is
    added to the return list. Every hierarchy will have its top level
    removed and entered into a dict, with the top-level hierarchy name as the
    key and the sub-nav as the value.

    Args:
        x (Nav): The list of NavEntry to process

    Returns:
        Tuple[List[str], Dict[str, Nav]]: Structure as explained above.

    """
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

    Args:
        nav (Nav): The list of NavEntry to convert to mkdocs.yml format

    Returns:
        Python object of the mkdocs.yml nav entry.

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


def add_nav_entry(mkdocs_settings, nav_entry: NavEntry) -> Any:
    """
    Add an additional entry to the Nav in mkdocs.yml

    Args:
        mkdocs_settings (): The mkdocs settings to update.
        nav_entry (NavEntry): The NavEntry to add

    Returns:
        The updated mkdocs_settings
    """
    mkdocs_settings = deepcopy(mkdocs_settings)
    nav = mkdocs_to_nav(mkdocs_settings["nav"]) + [nav_entry]
    # we need to deduplicate
    nav = list(unique_everseen(nav))
    mkdocs_nav = nav_to_mkdocs(nav)
    mkdocs_settings["nav"] = mkdocs_nav

    return mkdocs_settings


def load_yaml(file: Path) -> Any:
    """
    Load a yaml file, return empty dict if not exists.

    Args:
        file (Path): File to load

    Returns:
        The value in the file, empty dict otherwise.

    """
    if file.exists():
        with file.open("r") as f:
            res = yaml.load(f, Loader=yaml.Loader)
    else:
        res = {}

    return res


def save_yaml(obj: Any, file: Path) -> None:
    """
    Save object to yaml file.

    Args:
        obj (Any): The object to save.
        file (Path): Filename to save it into.
    """
    with file.open("w") as f:
        yaml.dump(obj, f, default_flow_style=False)
