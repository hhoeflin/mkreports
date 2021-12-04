import hashlib
import shutil
from copy import copy
from pathlib import Path
from typing import Literal, Optional

from md_obj import MdObj

from .text import Text


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
        relative_to: Optional[Path] = None,
        allow_copy: bool = True,
        hash: bool = False,
    ) -> None:
        super().__init__()
        self.path = path
        self.relative_to = Path.cwd() if relative_to is None else relative_to
        self.allow_copy = allow_copy
        self.hash = hash

    @property
    def abs_path(self) -> Path:
        if self.relative_to is None:
            return self.path.absolute()
        else:
            return (self.relative_to / self.path).absolute()

    def store(self, store_path: Path) -> "File":
        if self.allow_copy:

            if self.hash:
                # we calculate the hash of the file to be ingested
                path_hash = md5_hash_file(self.abs_path)
                new_path = store_path / (
                    self.path.stem + "-" + path_hash + self.path.suffix
                )
            else:
                new_path = store_path / self.path.name

            # now see if we move or copy the file
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.abs_path, new_path)

            new_file = copy(self)
            new_file.relative_to = None
            new_file.path = new_path
        else:
            new_file = self

        self._save(new_file)
        return new_file

    def localize(self, relative_to: Optional[Path] = None) -> "File":
        if relative_to is None:
            new_file = self
        else:
            new_file = copy(self)
            if self.path.is_absolute():
                new_obj.relative_to = relative_to
                new_obj.path = self.path.relative_to(relative_to)
                self._child = new_obj
                return self._child
            else:
                if self.relative_to == relative_to:
                    return self
                else:
                    new_obj.relative_to = relative_to
                    new_obj.path = (self.relative_to / self.path).relative_to(
                        relative_to
                    )
                    # path is already relative. Interpret it relative to cwd.
                    self._child = new_obj
                return self._child
        self._save(new_file)
        return new_file

    def require_localize(self) -> bool:
        return True


class ImageFile(File):
    def __init__(
        self, path: Path, text: str = "", relative_to: Optional[Path] = None
    ) -> None:
        super().__init__(path=path, relative_to=relative_to)

    def to_markdown(self) -> Text:
        pass
