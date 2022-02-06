import html
import textwrap
from dataclasses import dataclass
from pathlib import Path
from textwrap import indent
from typing import Literal, Optional, Tuple, Union

from mdutils.tools.TextUtils import TextUtils

from .base import MdObj, MdOut
from .file import File
from .settings import Settings
from .text import SpacedText, Text


@dataclass
class Admonition(MdObj):
    text: Union[Text, MdObj]
    title: Optional[str] = None
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

    def to_markdown(self, **kwargs) -> MdOut:
        if isinstance(self.text, MdObj):
            admon_text, back = self.text.to_markdown(**kwargs)
        else:
            admon_text, back = str(self.text), SpacedText()

        if self.title is None:
            title_md = ""
        else:
            title_md = f'"{self.title}"'

        return MdOut(
            body=SpacedText(
                f"{'???' if self.collapse else '!!!'} {self.kind} {title_md}",
                (2, 2),
            )
            + SpacedText(indent(str(admon_text), "    "), (2, 2)),
            back=back,
        )


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

    def to_markdown(self, **kwargs) -> MdOut:
        if isinstance(self.text, MdObj):
            tab_text, back = self.text.to_markdown(**kwargs)
        else:
            tab_text, back = str(self.text), SpacedText()

        if self.title is not None:
            title_text = html.escape(self.title)
        else:
            title_text = ""

        return MdOut(
            body=SpacedText(f'=== "{title_text}"', (2, 2))
            + SpacedText(indent(str(tab_text), "    "), (2, 2)),
            back=back,
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

    def req_settings(self):
        settings = Settings(
            mkdocs=dict(
                markdown_extensions=[{"pymdownx.highlight": dict(use_pygments=True)}]
            )
        )
        return settings

    def to_markdown(self, **kwargs) -> MdOut:
        del kwargs
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

        return MdOut(
            body=SpacedText(
                TextUtils.insert_code(textwrap.dedent(self.code), annots), (2, 2)
            )
        )


class CodeFile(File):
    """
    Code block with the content of a file.
    """

    def __init__(
        self,
        path: Path,
        store_path: Path,
        report_path: Path,
        title: Optional[str] = None,
        hl_lines: Optional[Tuple[int, int]] = None,
        language: Optional[str] = "python",
    ):
        """
        Move a code-file into the store-dir and reference it in code block.
        """
        super().__init__(
            path=path, store_path=store_path, allow_copy=True, use_hash=True
        )
        self.report_path = report_path
        self.title = title
        self.hl_lines = hl_lines
        self.language = language

    def req_settings(self):
        settings = Settings(mkdocs=dict(markdown_extensions="pymdownx.snippets"))
        settings = Settings(
            mkdocs=dict(
                markdown_extensions=[
                    "pymdownx.snippets",
                    {"pymdownx.highlight": dict(use_pygments=True)},
                ]
            )
        )
        return settings

    def to_markdown(self, **kwargs) -> MdOut:
        del kwargs
        annots = ""
        if self.language is not None:
            annots = annots + self.language
        if self.title is not None:
            annots = annots + f' title="{html.escape(self.title)}"'

        hl_lines = self.hl_lines
        if hl_lines is not None:
            annots = annots + f' hl_lines="{hl_lines[0]}-{hl_lines[1]}"'

        return MdOut(
            body=SpacedText(
                TextUtils.insert_code(
                    f"--8<-- '{self.path.relative_to(self.report_path)}'", annots
                ),
                (2, 2),
            )
        )
