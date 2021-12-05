"""
Various utility functions for the package.
"""
from copy import deepcopy
from pathlib import Path
from typing import Any, List, Mapping, Union

import yaml
from deepmerge import Merger

Nav = List[Union[str, "Nav", Mapping[str, Union[str, "Nav"]]]]


def snake_to_text(x: str) -> str:
    """Convert snake case to regular text, with each word capitalized."""
    return " ".join([w.capitalize() for w in x.split("_")])


def path_to_nav_entry(path: Path, orig_path=None) -> Nav:
    # remember the original path to use
    if orig_path is None:
        orig_path = path
    if len(path.parts) == 1:
        return [{snake_to_text(path.stem): str(orig_path)}]
    else:
        outer = path.parts[0]
        rest = Path(*path.parts[1:])
        return [{snake_to_text(outer): path_to_nav_entry(rest, orig_path=orig_path)}]


def check_length_one(x: Union[List, Mapping]) -> Any:
    if isinstance(x, List):
        assert len(x) == 1
        return x[0]
    elif isinstance(x, Mapping):
        assert len(x) == 1
        return list(x.values())[0]
    else:
        raise ValueError("Unexpected type")


def path_from_nav_entry(x: Nav) -> Path:
    # first unpack the list
    x_entry = check_length_one(x)
    if isinstance(x_entry, str):
        return Path(x_entry)
    elif isinstance(x_entry, Mapping):
        value = check_length_one(x_entry)
        if isinstance(value, str):
            return Path(value)
        elif isinstance(value, List):
            return path_from_nav_entry(check_length_one(x_entry))
        else:
            raise ValueError("Not a nav item as defined")
    elif isinstance(x_entry, List):
        return path_from_nav_entry(check_length_one(x_entry))
    else:
        raise ValueError("Not a nav item as defined")


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


def update_mkdocs(mkdocs_file: Path, nav_entry: Nav) -> None:
    # now we read the mkdocs yaml file
    # merge the nav entry in it with the new one
    # and write it out
    with mkdocs_file.open("r") as f:
        mkdocs_settings = yaml.load(f, Loader=yaml.Loader)

    nav = deepcopy(mkdocs_settings["nav"])
    nav = nav_merger.merge(nav, nav_entry)
    mkdocs_settings["nav"] = nav

    with mkdocs_file.open("w") as f:
        yaml.dump(mkdocs_settings, f, default_flow_style=False)
