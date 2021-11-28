"""
Class representing a page in the final report.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from .utils import md5_hash_file


class Page:
    def __init__(self, path: Path, report: "Report") -> None:
        self._path = path
        self._report = report

    @property
    def path(self) -> Path:
        return self._path

    @property
    def report(self) -> "Report":
        return self._report

    @property
    def abs_path(self) -> Path:
        return (self._report.docs_dir / self._path).resolve()

    @property
    def gen_asset_path(self) -> Path:
        return self.abs_path.parent / (self._path.stem + "_gen_assets")

    def ingest_asset(self, path: Path, move: bool = False, hash: bool = True) -> Path:

        if hash:
            # we calculate the hash of the file to be ingested
            path_hash = md5_hash_file(path)
            new_path = self.gen_asset_path / (path.stem + "-" + path_hash + path.suffix)
        else:
            new_path = self.gen_asset_path / path.name

        # now see if we move or copy the file
        new_path.parent.mkdir(parents=True, exist_ok=True)
        if move:
            shutil.move(path, new_path)
        else:
            shutil.copy(path, new_path)

        return new_path.relative_to(self.abs_path.parent)
