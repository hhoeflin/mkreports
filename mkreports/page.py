"""
Class representing a page in the final report.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Union

from .md import Counters, MdObj, SpacedText, Text


class Page:
    def __init__(self, path: Path, report: "Report") -> None:
        self._path = path
        self._report = report
        self._counters = Counters()

        # get the last string that was written into the page (if it exists)
        # otherwise we set it to newlines.
        if self.page_abs_path.exists():
            with self.page_abs_path.open("r") as f:
                last_lines = f.readlines()[-3:]
            self._last_obj = SpacedText("".join(last_lines))
        else:
            self._last_obj = SpacedText("\n\n\n")

    @property
    def path(self) -> Path:
        return self._path

    @property
    def report(self) -> "Report":
        return self._report

    @property
    def page_abs_path(self) -> Path:
        return (self._report.docs_dir / self._path).resolve()

    @property
    def gen_asset_path(self) -> Path:
        return self.page_abs_path.parent / (self._path.stem + "_gen_assets")

    def clear(self) -> None:
        """Clear the page markdown file and the generated assets directory."""
        shutil.rmtree(self.gen_asset_path)
        self.page_abs_path.unlink()

    def append(self, item: Union[MdObj, Text]) -> None:
        if isinstance(item, MdObj):
            md_text = item.process_all(
                store_path=self.gen_asset_path,
                page_path=self.page_abs_path,
                counters=self._counters,
            )
        elif isinstance(item, (str, SpacedText)):
            md_text = SpacedText(item)
        else:
            raise Exception("item should be a str, SpacedText or MdObj")

        with self.page_abs_path.open("a") as f:
            f.write(md_text.format_text(self._last_obj, "a"))
