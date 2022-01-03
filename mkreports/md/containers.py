import html
import textwrap
from dataclasses import dataclass
from pathlib import Path
from textwrap import indent
from typing import Literal, Optional, Tuple, Union

from mdutils.tools.TextUtils import TextUtils
from mkreports.settings import Settings

from .base import MdObj
from .text import SpacedText, Text


@dataclass
class Admonition(MdObj):
    text: Union[Text, MdObj]
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
    ] = "note"
    collapse: bool = False

    def req_settings(self) -> Settings:
        cont_settings = Settings(
            mkdocs={
                "markdown_extensions": [
                    "admonition",
                    "pymdownx.details",
                    "pymdownx.superfences",
                ]
            }
        )
        if isinstance(self.text, MdObj):
            return cont_settings + self.text.req_settings()
        else:
            return cont_settings

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

        return SpacedText(
            f"{'???' if self.collapse else '!!!'} {self.kind}", (2, 2)
        ) + SpacedText(indent(str(admon_text), "    "), (2, 2))


@dataclass
class Tab(MdObj):
    text: Union[Text, MdObj]
    title: Optional[str] = None

    def req_settings(self) -> Settings:
        tab_settings = Settings(
            mkdocs={
                "markdown_extensions": [
                    "pymdownx.superfences",
                    {"pymdownx.tabbed": {"alternate_style": True}},
                ]
            }
        )
        if isinstance(self.text, MdObj):
            return tab_settings + self.text.req_settings()
        else:
            return tab_settings

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

        if self.title is not None:
            title_text = html.escape(self.title)
        else:
            title_text = ""

        return SpacedText(f'=== "{title_text}"', (2, 2)) + SpacedText(
            indent(str(tab_text), "    "), (2, 2)
        )


@dataclass(frozen=True)
class Code(MdObj):
    """Wrapper class for code."""

    code: str
    title: Optional[str] = None
    first_line: Optional[int] = None
    hl_lines: Optional[Tuple[int, int]] = None
    language: Optional[str] = "python"
    dedent: bool = True

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        annots = ""
        if self.language is not None:
            annots = annots + self.language
        if self.title is not None:
            annots = annots + f' title="{html.escape(self.title)}"'
        if self.first_line is not None:
            # hi_lines get intrepreted relative to first_line
            if self.hl_lines is not None:
                hl_lines = (
                    self.hl_lines[0] - self.first_line + 1,
                    self.hl_lines[1] - self.first_line + 1,
                )
            else:
                hl_lines = self.hl_lines
            annots = annots + f' linenums="{self.first_line}"'
        else:
            hl_lines = self.hl_lines

        if hl_lines is not None:
            annots = annots + f' hl_lines="{hl_lines[0]}-{hl_lines[1]}"'

        return SpacedText(
            TextUtils.insert_code(textwrap.dedent(self.code), annots), (2, 2)
        )
