from pathlib import Path
from typing import Optional

from .base import MdObj, MdOut
from .settings import Settings
from .text import SpacedText


class Docstring(MdObj):
    def __init__(self, obj_name: str) -> None:
        super().__init__()
        self.obj_name = obj_name

    def req_settings(self) -> Settings:
        cont_settings = Settings(
            mkdocs={
                "plugins": [
                    "search",
                    "mkdocstrings",
                ]
            }
        )
        return cont_settings

    def to_markdown(self, page_path: Optional[Path] = None) -> MdOut:
        del page_path
        return MdOut(body=SpacedText(f"::: {self.obj_name}", (2, 2)))
