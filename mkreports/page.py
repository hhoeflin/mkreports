"""
Class representing a page in the final report.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Union

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

        return new_path.relative_to(self.abs_path.parent)

    def clear(self) -> None:
        """Clear the page markdown file and the generated assets directory."""
        shutil.rmtree(self.gen_asset_path)
        self.abs_path.unlink()

    def append(item: Union[str, MdBlob]) -> None:
        pass
