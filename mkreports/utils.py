import json
from pathlib import Path
from typing import Any, Optional, Set, Union

import parse  # type: ignore
from git.repo import Repo


def repo_root(path: Path = Path(".")) -> Optional[Path]:
    """
    Find the root of the current repository.

    Args:
        path (Path): A path in the repository.

    Returns:
        Optional[Path]: The root of the repo if it is a repo, None otherwise.

    """
    try:
        repo = Repo(path, search_parent_directories=True)
        if repo.working_tree_dir is not None:
            return Path(repo.working_tree_dir)
        else:
            return None
    except Exception:
        pass

    return None


def relative_repo_root(path: Union[Path, str]) -> str:
    """
    Path relative to repo root or just the name.

    Args:
        path (Union[Path, str]): Path to analyze

    Returns:
        str: Path relative to the repo root, just the name otherwise.

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
    """
    Identify ids in a file.

    We encode IDs used in a file in markdown comments to make
    them easier to find. This function retrieves them.

    Args:
        text (str): The string to search for the IDs.

    Returns:
        Set[str]: A set with all identified IDs.

    """
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


def func_ref(x: str) -> str:
    """
    Encode a function reference.

    Args:
        x (str): reference to a function.

    Returns:
        The encoded string.

    """
    return f"____{x}____"


def serialize_json(obj: Any) -> str:
    """Serialize an object to JSON, removing quotes for special strings."""
    return json.dumps(obj).replace('"____', "").replace('____"', "")
