from pathlib import Path
from textwrap import indent
from typing import Literal, Optional, Union

from mkreports.settings import Settings

from .base import MdObj
from .text import SpacedText, Text


class Admonition(MdObj):
    def __init__(
        self,
        text: Union[Text, MdObj],
        kind: Literal[
            "note",
            "abstract",
            "info",
            "tip",
            "success",
            "question",
            "warning",
            "failure",
            "danger",
            "bug",
            "example",
            "quote",
        ] = "note",
        collapse: bool = False,
    ):
        self.text = text
        self.kind = kind
        self.collapse = collapse

    def req_settings(self) -> Settings:
        return Settings(
            mkdocs={
                "markdown_extensions": [
                    "admonition",
                    "pymdownx.details",
                    "pymdownx.superfences",
                ]
            }
        )

    def backmatter(self, page_path: Optional[Path] = None):
        if isinstance(self.text, MdObj):
            return self.text.backmatter(page_path)
        else:
            return SpacedText("")

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        if isinstance(self.text, MdObj):
            admon_text = self.text.to_markdown(page_path)
        else:
            admon_text = str(self.text)

        return SpacedText(f"{'???' if self.collapse else '!!!'} {self.kind}", (2, 2)) + SpacedText(
            indent(str(admon_text), "    "), (2, 2)
        )


class Tab(MdObj):
    def __init__(self, text: Union[Text, MdObj], title: Optional[str] = None):
        self.text = text
        self.title = title

    def req_settings(self) -> Settings:
        return Settings(
            mkdocs={
                "markdown_extensions": [
                    "pymdownx.superfences",
                    {"pymdownx.tabbed": {"alternate_style": True}},
                ]
            }
        )

    def backmatter(self, page_path: Optional[Path] = None):
        if isinstance(self.text, MdObj):
            return self.text.backmatter(page_path)
        else:
            return SpacedText("")

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        if isinstance(self.text, MdObj):
            tab_text = self.text.to_markdown(page_path)
        else:
            tab_text = str(self.text)

        return SpacedText(f'=== "{self.title}"', (2, 2)) + SpacedText(indent(str(tab_text), "    "), (2, 2))
