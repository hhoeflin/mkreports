import os
from pathlib import Path
from typing import ClassVar, Optional

from git.repo import Repo
from platformdirs import user_state_path


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
        if repo.working_tree_dir is None:
            return None
        else:
            return Path(repo.working_tree_dir)
    except Exception:
        pass

    return None


def search_mkreports_upwards() -> Optional[Path]:
    """
    Search for a '.mkreports' directory upwards.
    """
    cur_dir = Path.cwd()

    while True:
        if (cur_dir / ".mkreports").exists():
            return cur_dir / ".mkreports"
        if cur_dir.parent == cur_dir:
            return None
        else:
            cur_dir = cur_dir.parent


def default_mkreports_dir() -> Path:
    """
    Function to set the default mkreports dir.

    The rule for finding the default directory is as follows:
        - Whatever the MKREPORTS_ROOT_DIR is set to, if it is set
        - any '.mkreports' directory in the current or any parent directory
        - a 'mkreports' directory in 'XDG_STATE_HOME' or `~/.local/state/mkreports' if it is
          not set. This one will be set if no others are available
    """
    if (mkreports_dir_str := os.environ.get("MKREPORTS_ROOT_DIR", "")) != "":
        return Path(mkreports_dir_str)
    elif (mkreports_dir := search_mkreports_upwards()) is not None:
        return mkreports_dir
    else:
        mkreports_dir = user_state_path("mkreports")
        mkreports_dir.mkdir(parents=True, exist_ok=True)
        return mkreports_dir


class Config:
    mkreports_dir: ClassVar[Path] = default_mkreports_dir()
