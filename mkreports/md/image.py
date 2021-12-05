import hashlib
import shutil
from copy import copy
from pathlib import Path
from typing import Optional

from .base import MdObj
from .text import SpacedText


def md5_hash_file(path: Path) -> str:
    m = hashlib.md5()
    with path.open("rb") as f:
        m.update(f.read())

    return m.hexdigest()


class File(MdObj):

    path: Path
    relative_to: Optional[Path]

    def __init__(
        self,
        path: Path,
        store_path: Path,
        allow_copy: bool = True,
        hash: bool = False,
    ) -> None:
        super().__init__()
        self.path = path.absolute()

        self.allow_copy = allow_copy
        self.hash = hash
        self.store_path = store_path

        if self.allow_copy:

            if self.hash:
                # we calculate the hash of the file to be ingested
                path_hash = md5_hash_file(self.path)
                new_path = store_path / (
                    self.path.stem + "-" + path_hash + self.path.suffix
                )
            else:
                new_path = store_path / self.path.name

            # now see if we move or copy the file
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.path, new_path)
            self.path = new_path
        else:
            new_file = self

    def to_markdown(self, page_path: Path) -> SpacedText:
        return SpacedText("")


class ImageFile(File):
    def __init__(
        self,
        path: Path,
        text: str = "",
        tooltip: str = "",
    ) -> None:
        super().__init__(path=path)
        self.text = text
        self.tooltip = tooltip

    def to_markdown(self, path: Path) -> SpacedText:

        pass
