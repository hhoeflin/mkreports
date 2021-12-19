import hashlib
import shutil
from pathlib import Path
from typing import Optional

from .base import MdObj, get_default_store_path
from .text import SpacedText


def true_stem(path: Path) -> str:
    """True stem of a path, without all suffixes, not just last."""
    return path.name[: -(len("".join(path.suffixes)))]


def md5_hash_file(path: Path) -> str:
    m = hashlib.md5()
    with path.open("rb") as f:
        m.update(f.read())

    return m.hexdigest()


def relpath(path_to, path_from):
    path_to = Path(path_to).absolute()
    path_from = Path(path_from).absolute()
    head = Path("/")
    tail = Path("")
    try:
        for p in (*reversed(path_from.parents), path_from):
            head, tail = p, path_to.relative_to(p)
    except ValueError:  # Stop when the paths diverge.
        pass
    return Path("../" * (len(path_from.parents) - len(head.parents))).joinpath(tail)


class File(MdObj):

    path: Path
    relative_to: Optional[Path]

    def __init__(
        self,
        path: Path,
        store_path: Optional[Path] = None,
        allow_copy: bool = True,
        hash: bool = False,
    ) -> None:
        super().__init__()
        self.path = path.absolute()

        self.allow_copy = allow_copy
        self.hash = hash
        self.store_path = (
            store_path if store_path is not None else get_default_store_path()
        )

        if self.store_path is None:
            raise ValueError("store_path or a default must be set. Can't both be None.")

        if self.allow_copy:

            if self.hash:
                # we calculate the hash of the file to be ingested
                path_hash = md5_hash_file(self.path)
                new_path = self.store_path / (
                    true_stem(self.path) + "-" + path_hash + "".join(self.path.suffixes)
                )
            else:
                new_path = self.store_path / self.path.name

            # now see if we move or copy the file
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.path, new_path)
            self.path = new_path
        else:
            pass

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        return SpacedText("")
