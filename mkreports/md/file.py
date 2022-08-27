import hashlib
import shutil
import sys
from os.path import relpath
from pathlib import Path
from typing import Optional, Set, Union

import importlib_resources as imp_res

from .base import MdObj, NotRenderedError, RenderedMd, func_kwargs_as_set
from .md_proxy import register_md

if sys.version_info < (3, 9):
    import importlib_resources as imp_res
else:
    import importlib.resources as imp_res


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


def store_asset_relpath(
    asset_path_mkreports: Path, javascript_path: Path, page_path: Path
) -> str:
    """
    Store an asset and return relative path to it.

    Args:
        asset_path (Path): Relative asset path inside 'mkreports'

    Returns:
        str: Path to the asset as it should be used from html
    """
    asset_path_report_abs = javascript_path / "assets" / asset_path_mkreports.name
    asset_path_report_abs.parent.mkdir(parents=True, exist_ok=True)
    with imp_res.as_file(
        imp_res.files("mkreports") / "assets" / asset_path_mkreports
    ) as asset_file:
        shutil.copy(
            str(asset_file),
            str(asset_path_report_abs),
        )
    return relpath_html(asset_path_report_abs, page_path)


@register_md("File")
class File(MdObj):
    """
    A stored file.

    This is typically not needed by the end-user.
    """

    _path: Optional[Path]
    allow_copy: bool
    use_hash: bool
    _hash: Optional[str] = None

    def __init__(
        self,
        path: Union[str, Path],
        allow_copy: bool = True,
        use_hash: bool = False,
    ) -> None:
        """
        Store a file in the page-store.

        Args:
            path (Union[str, Path]): Path to the file,
                relative to current directory or absolute.
            allow_copy (bool): Is the file allowed to be copied? Otherwise, original
                location is used.
            use_hash (bool): If copy is allowed, renames the file to include the file hash.
        """
        super().__init__()

        # store path needs to be set

        # set the existing attributes
        self.allow_copy = allow_copy
        self.use_hash = use_hash

        # for the path we first have to see if they will be copied
        if not self.allow_copy:
            self._path = Path(path).absolute()
        else:
            self._path = None
            self._file_binary = Path(path).read_bytes()
            self._orig_path = Path(path).absolute()

    @property
    def path(self) -> Path:
        if self._path is None:
            raise NotRenderedError("Not yet rendered")
        else:
            return self._path

    def _render(self, store_path: Path) -> RenderedMd:
        if self.allow_copy:

            if self.use_hash:
                # we calculate the hash of the file to be ingested
                new_path = store_path / (
                    true_stem(self._orig_path)
                    + "-"
                    + hashlib.md5(self._file_binary).hexdigest()
                    + "".join(self._orig_path.suffixes)
                )
            else:
                new_path = store_path / self.path.name

            # now see if we move or copy the file
            new_path.parent.mkdir(parents=True, exist_ok=True)
            with new_path.open("wb") as f:
                f.write(self._file_binary)
            self._path = new_path

        return RenderedMd(body=None, back=None, settings=None, src=self)

    def render_fixtures(self) -> Set[str]:
        return func_kwargs_as_set(self._render)
