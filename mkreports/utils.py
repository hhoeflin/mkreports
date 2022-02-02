from pathlib import Path
from typing import Union

import git


def relative_repo_root(path: Union[Path, str]) -> str:
    """
    Path relative to repo root or just the name.
    """
    try:
        repo = git.Repo(".", search_parent_directories=True)
        root_dir = repo.working_tree_dir
        if root_dir is not None:
            return str(Path(path).relative_to(root_dir))

    except Exception:
        pass

    return Path(path).name
