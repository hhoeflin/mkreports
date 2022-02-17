import html
import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path
from textwrap import indent
from typing import Literal, Optional, Tuple, Union

from mdutils.tools.TextUtils import TextUtils
from mkreports.md_proxy import register_md

from .base import MdObj
from .file import File, relpath_html
from .settings import Settings
from .text import SpacedText, Text


@register_md("Admonition")
@dataclass
class Admonition(MdObj):
    text: Union[Text, MdObj]
    page_path: Path
    javascript_path: Path
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
        "code",
    ] = "note"
    collapse: bool = False

    def __post_init__(self):
        if self.kind == "code":
            # create a css file that creates a 'code' admonition
            self.css_path = self.javascript_path / "code_admonition.css"
            self.javascript_path.mkdir(parents=True, exist_ok=True)
            shutil.copy(
                Path(__file__).parent / "code_admonition.css",
                self.css_path,
            )

        # if code-admonition, we need to load additional css
        if self.kind == "code":
            rel_css_path = relpath_html(self.css_path, self.page_path)
            page_settings = dict(css=[rel_css_path])
        else:
            page_settings = {}
        cont_settings = Settings(
            mkdocs={
                "markdown_extensions": [
                    "admonition",
                    "pymdownx.details",
                    "pymdownx.superfences",
                ]
            },
            page=page_settings,
        )
        if isinstance(self.text, MdObj):
            admon_text = self.text.body
            back = self.text.back
            settings = self.text.settings
            settings = cont_settings + settings
        else:
            admon_text, back, settings = str(self.text), SpacedText(), cont_settings

        if self.title is None:
            title_md = ""
        else:
            title_md = f'"{self.title}"'

        self._body = SpacedText(
            f"{'???' if self.collapse else '!!!'} {self.kind} {title_md}", (2, 2)
        ) + SpacedText(indent(str(admon_text), "    "), (2, 2))
        self._back = back
        self._settings = settings


@register_md("Tab")
@dataclass
class Tab(MdObj):
    text: Union[Text, MdObj]
    title: Optional[str] = None

    def __post_init__(self):
        tab_settings = Settings(
            mkdocs={
                "markdown_extensions": [
                    "pymdownx.superfences",
                    {"pymdownx.tabbed": {"alternate_style": True}},
                ]
            }
        )
        if isinstance(self.text, MdObj):
            tab_text = self.text.body
            back = self.text.back
            settings = self.text.settings
            settings = tab_settings + settings
        else:
            tab_text, back, settings = str(self.text), SpacedText(), tab_settings

        if self.title is not None:
            title_text = html.escape(self.title)
        else:
            title_text = ""

        self._body = SpacedText(f'=== "{title_text}"', (2, 2)) + SpacedText(
            indent(str(tab_text), "    "), (2, 2)
        )
        self._back = back
        self._settings = settings


@register_md("Code")
@dataclass
class Code(MdObj):
    """Wrapper class for code."""

    code: str
    title: Optional[str] = None
    first_line: Optional[int] = None
    hl_lines: Optional[Tuple[int, int]] = None
    language: Optional[str] = "python"
    dedent: bool = True

    def __post_init__(self):
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

        settings = Settings(
            mkdocs=dict(
                markdown_extensions=[{"pymdownx.highlight": dict(use_pygments=True)}]
            )
        )
        self._body = SpacedText(
            TextUtils.insert_code(textwrap.dedent(self.code), annots), (2, 2)
        )
        self._back = None
        self._settings = settings


@register_md("CodeFile")
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

        annots = ""
        if self.language is not None:
            annots = annots + self.language
        if self.title is not None:
            annots = annots + f' title="{html.escape(self.title)}"'

        hl_lines = self.hl_lines
        if hl_lines is not None:
            annots = annots + f' hl_lines="{hl_lines[0]}-{hl_lines[1]}"'

        settings = Settings(
            mkdocs=dict(
                markdown_extensions=[
                    "pymdownx.snippets",
                    {"pymdownx.highlight": dict(use_pygments=True)},
                ]
            )
        )
        self._body = SpacedText(
            TextUtils.insert_code(
                f"--8<-- '{self.path.relative_to(self.report_path)}'", annots
            ),
            (2, 2),
        )
        self._back = None
        self._settings = settings
