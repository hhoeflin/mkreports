import html
import textwrap
from dataclasses import dataclass
from pathlib import Path
from textwrap import indent
from typing import Literal, Optional, Tuple, Union

from mdutils.tools.TextUtils import TextUtils

from .base import MdObj
from .file import File, store_asset_relpath
from .md_proxy import register_md
from .settings import PageInfo, Settings
from .text import SpacedText, Text


@register_md("Admonition")
@dataclass
class Admonition(MdObj):
    """
    An admonition to be added to a page. Can also be collapsed. For more
    details see also the Materials-theme for mkdocs.

    Args:
        obj (Union[MdObj, Text]): object in the admonition. Markdown object, string
            or SpacedText.
        title (Optional[str]): title shown in the admonition. If missing, defaults
            to 'kind'.
        kind (Literal[ 'note', 'abstract', 'info', 'tip', 'success', 'question', 'warning', 'failure', 'danger', 'bug', 'example', 'quote', 'code']): The type of
            admonition to be shown. See also the Materials-theme for mkdocs for
            more details.
        collapse (bool): Should the admonition be collapsed?
        page_info (Optional[PageInfo]): Only needed when 'kind=="code"'.
    """

    obj: Union[Text, MdObj]
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
    page_info: Optional[PageInfo] = None

    def __post_init__(self):
        assert self.page_info is not None
        # if code-admonition, we need to load additional css
        if self.kind == "code":
            rel_css_path = store_asset_relpath(
                Path("code_admonition.css"), self.page_info
            )
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
        if isinstance(self.obj, MdObj):
            admon_text = self.obj.body
            back = self.obj.back
            settings = self.obj.settings
            settings = cont_settings + settings
        else:
            admon_text, back, settings = str(self.obj), SpacedText(), cont_settings

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
    """
    Tab interface

    Args:
        obj (Union[Text, MdObj]): The object to be shown in the tab. An MdObj,
            string or SpacedText.
        title (Optional[str]): Optional title for the tab.
    """

    obj: Union[Text, MdObj]
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
        if isinstance(self.obj, MdObj):
            tab_text = self.obj.body
            back = self.obj.back
            settings = self.obj.settings
            settings = tab_settings + settings
        else:
            tab_text, back, settings = str(self.obj), SpacedText(), tab_settings

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
    """
    Shows a code-block.

    Args:
        code (str): The code to be shown as a string.
        title (Optional[str]): Optional title for the code block.
        first_line (Optional[int]): Number at the first line.
        hl_lines (Optional[Tuple[int, int]]): Line-range for highlighting.
            Is counted relative to 'first_line'.
        language (Optional[str]): Language for syntax highlighting.
        dedent (bool): Should the string be de-dented?

    """

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
        path: Union[Path, str],
        page_info: PageInfo,
        title: Optional[str] = None,
        hl_lines: Optional[Tuple[int, int]] = None,
        language: Optional[str] = "python",
    ):
        """
        Set up the code-block with file content.

        Args:
            path (Union[Path, str]): Abolute path or relative to current working dir for the
                code-file to be included.
            page_info (PageInfo): PageInfo on the page where the code is to be added.
            title (Optional[str]): Title of the code-block. If 'None', the path of the
                code file relative to the project root will be added. If it should be
                empty, set to empty string.
            hl_lines (Optional[Tuple[int, int]]): Optional range of lines for highlighting.
            language (Optional[str]): Language for syntax highlighting.
        """
        assert page_info.project_root is not None
        assert page_info.report_path is not None

        path = Path(path)

        super().__init__(path=path, page_info=page_info, allow_copy=True, use_hash=True)
        self.title = (
            title
            if title is not None
            else str(path.relative_to(page_info.project_root))
        )
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
                f"--8<-- '{self.path.relative_to(page_info.report_path)}'", annots
            ),
            (2, 2),
        )
        self._back = None
        self._settings = settings
