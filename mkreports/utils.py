"""
Various utility functions for the package.
"""
import hashlib
from copy import deepcopy
from pathlib import Path
from typing import List, Mapping, Union

import yaml
from deepmerge import Merger

NavEntry = Union[Mapping[str, "NavEntry"], List["NavEntry"], str]


def snake_to_text(x: str) -> str:
    """Convert snake case to regular text, with each word capitalized."""
    return " ".join([w.capitalize() for w in x.split("_")])


def path_to_nav_entry(path: Path, orig_path=None) -> NavEntry:
    # remember the original path to use
    if orig_path is None:
        orig_path = path
    if len(path.parts) == 1:
        return {snake_to_text(path.stem): str(orig_path)}
    else:
        outer = path.parts[0]
        rest = Path(*path.parts[1:])
        return {snake_to_text(outer): path_to_nav_entry(rest)}


def path_from_nav_entry(x: NavEntry) -> Path:
    if isinstance(x, (Mapping, List)):
        if isinstance(x, Mapping):
            values = list(x.values())
        else:
            values = x
        if len(values) != 1:
            raise ValueError("Dictionary or list should only have 1 entry")
        else:
            return path_from_nav_entry(values[0])
    else:
        return Path(x)


def str_as_list_append(config, path, base, nxt):
    return [base] + nxt


nav_merger = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [
        (list, ["append"]),
        (dict, ["merge"]),
        (set, ["union"]),
        (str, [str_as_list_append]),
    ],
    # next, choose the fallback strategies,
    # applied to all other types:
    ["override"],
    # finally, choose the strategies in
    # the case where the types conflict:
    ["override"],
)


def update_mkdocs(mkdocs_file: Path, nav_entry: NavEntry) -> None:
    # now we read the mkdocs yaml file
    # merge the nav entry in it with the new one
    # and write it out
    with mkdocs_file.open("r") as f:
        mkdocs_settings = yaml.load(f, Loader=yaml.Loader)

    nav = deepcopy(mkdocs_settings["nav"])
    nav_merger.merge(nav, nav_entry)
    mkdocs_settings["nav"] = nav

    with mkdocs_file.open("w") as f:
        yaml.dump(mkdocs_settings, f, default_flow_style=False)


def md5_hash_file(path: Path) -> str:
    m = hashlib.md5()
    with path.open("rb") as f:
        m.update(f.read())

    return m.hexdigest()
