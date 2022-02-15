import hashlib
from mkreports.md_proxy import register_md
import shutil
from os.path import relpath
from pathlib import Path
from typing import Optional, Union

from .base import MdObj, MdOut


def true_stem(path: Path) -> str:
    """True stem of a path, without all suffixes, not just last."""
    return path.name[: -(len("".join(path.suffixes)))]


def md5_hash_file(path: Path) -> str:
    m = hashlib.md5()
    with path.open("rb") as f:
        m.update(f.read())

    return m.hexdigest()


def relpath_html(target: Path, page_path: Path):
    """
    Relative path as to be used for html
    """
    if page_path.stem == "index":
        # here, for translating to html, this path is referred to as its parent
        return relpath(target, page_path.parent)
    else:
        # for translating to html, will be converted to path.parent / path.stem / index.html
        return relpath(target, page_path)

@register_md('File')
class File(MdObj):

    path: Path
    allow_copy: bool
    store_path: Path
    use_hash: bool
    _hash: Optional[str] = None

    def __init__(
        self,
        path: Union[str, Path],
        store_path: Path,
        allow_copy: bool = True,
        use_hash: bool = False,
    ) -> None:
        super().__init__()

        # set the existing attributes
        self.allow_copy = allow_copy
        self.use_hash = use_hash
        self.store_path = store_path

        # for the path we first have to see if they will be copied
        self.path = Path(path).absolute()

        if self.allow_copy:

            if self.use_hash:
                # we calculate the hash of the file to be ingested
                new_path = self.store_path / (
                    true_stem(self.path) + "-" + self.hash + "".join(self.path.suffixes)
                )
            else:
                new_path = self.store_path / self.path.name

            # now see if we move or copy the file
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(path, new_path)
            self.path = new_path

    @property
    def hash(self) -> str:
        if self._hash is None:
            self._hash = md5_hash_file(self.path)
        return self._hash

    def to_markdown(self, page_path: Optional[Path] = None) -> MdOut:
        del page_path
        return MdOut()
