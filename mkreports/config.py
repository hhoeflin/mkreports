import hashlib
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

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
        if repo.working_tree_dir is None:
            return None
        else:
            return Path(repo.working_tree_dir)
    except Exception:
        pass

    return None


def set_mkreports_dir(
    mkreports_dir: Optional[Path] = None,
    repo_root_dir: Optional[Path] = repo_root(Path(os.getcwd())),
    mkreports_root_dir: Path = Path(
        os.environ.get("MKREPORTS_ROOT_DIR", Path(tempfile.gettempdir()) / "mkreports")
    ),
):
    """
    Function to derive the ckpt directory.

    This is called once at initialization. The reason is that it could change
    if the working directory is changed and this would be undesirable
    behavior.
    """
    if mkreports_dir is None:
        if repo_root_dir is None:
            mkreports_dir = mkreports_root_dir / "default"
        else:
            hash_str = hashlib.md5(str(repo_root_dir.resolve()).encode()).hexdigest()
            mkreports_dir = mkreports_root_dir / hash_str

    state["mkreports_dir"] = mkreports_dir


def get_mkreports_dir() -> Path:
    return state["mkreports_dir"]


# the mkreports_directory to use
state: Dict[str, Any] = dict()
set_mkreports_dir()
