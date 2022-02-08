from collections import defaultdict
from pathlib import Path
from typing import Set, Union

import parse
from git.repo import Repo


def relative_repo_root(path: Union[Path, str]) -> str:
    """
    Path relative to repo root or just the name.
    """
    try:
        repo = Repo(".", search_parent_directories=True)
        root_dir = repo.working_tree_dir
        if root_dir is not None:
            return str(Path(path).relative_to(root_dir))

    except Exception:
        pass

    return Path(path).name


def find_comment_ids(text: str) -> Set[str]:
    text_split = text.split("\n")

    # compile the parser
    comment_parser = parse.compile("[comment]: # (id: {type}-{value})")

    found_ids = []
    # get all occurences of an id, identify id-type and id-value
    for line in text_split:
        res = comment_parser.parse(line)
        if res is not None:
            assert isinstance(res, parse.Result)
            found_ids.append(f"{res['type']}-{res['value']}")

    return set(found_ids)


def snake_to_text(x: str) -> str:
    """Convert snake case to regular text, with each word capitalized."""
    return " ".join([w.capitalize() for w in x.split("_")])
