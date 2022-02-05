from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Union

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


def find_comment_ids(text: str) -> Dict[str, List[str]]:
    text_split = text.split("\n")

    # compile the parser
    comment_parser = parse.compile("[comment]: # (id: {type}-{value})")

    found_ids = defaultdict(list)
    # get all occurences of an id, identify id-type and id-value
    for line in text_split:
        res = comment_parser.parse(line)
        if res is not None:
            assert isinstance(res, parse.Result)
            found_ids[res["type"]].append(res["value"])

    return found_ids
