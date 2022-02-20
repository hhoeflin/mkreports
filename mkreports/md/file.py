import hashlib
import shutil
from os.path import relpath
from pathlib import Path
from typing import Optional, Union

from .base import MdObj
from .md_proxy import register_md
from .settings import PageInfo


def true_stem(path: Path) -> str:
    """True stem of a path, without all suffixes, not just last."""
    return path.name[: -(len("".join(path.suffixes)))]


def md5_hash_file(path: Path) -> str:
    """
    Get md5 hash of a file.

    Args:
        path (Path): Absolute path or relative to current directory of the file.

    Returns:
        str: The md5 hash of the file.

    """
    m = hashlib.md5()
    with path.open("rb") as f:
        m.update(f.read())

    return m.hexdigest()


def relpath_html(target: Path, page_path: Path) -> str:
    """
    Relative path as to be used for html. This is a bit more complicated,
    as some markdown pages are encoded as a directory (with implicit index.html
    being called).

    The paths can be relative or absolute. If relative, should be relative to
    same directory.

    Args:
        target (Path): The target path
        page_path (Path): Path of the current page.

    Returns:
        str: Relative path as a string.

    """
    if page_path.stem == "index":
        # here, for translating to html, this path is referred to as its parent
        return relpath(target, page_path.parent)
    else:
        # for translating to html, will be converted to path.parent / path.stem / index.html
        return relpath(target, page_path)


@register_md("File")
class File(MdObj):
    """
    A stored file.

    This is typically not needed by the end-user.
    """

    path: Path
    allow_copy: bool
    use_hash: bool
    _hash: Optional[str] = None

    def __init__(
        self,
        path: Union[str, Path],
        page_info: PageInfo,
        allow_copy: bool = True,
        use_hash: bool = False,
    ) -> None:
        """
        Store a file in the page-store.

        Args:
            path (Union[str, Path]): Path to the file,
                relative to current directory or absolute.
            page_info (PageInfo): PageInfo for the page where the file should be stored.
            allow_copy (bool): Is the file allowed to be copied? Otherwise, original
                location is used.
            use_hash (bool): If copy is allowed, renames the file to include the file hash.
        """
        super().__init__()

        # store path needs to be set
        assert page_info.store_path is not None

        # set the existing attributes
        self.allow_copy = allow_copy
        self.use_hash = use_hash
        self.store_path = page_info.store_path

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

        # it returns nothing
        self._body = None
        self._back = None
        self._settings = None

    @property
    def hash(self) -> str:
        """
        Calculate the hash of the file.

        Returns:
            str: Md5-hash as a string.

        """
        if self._hash is None:
            self._hash = md5_hash_file(self.path)
        return self._hash
