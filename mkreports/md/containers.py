import html
import textwrap
from dataclasses import dataclass
from pathlib import Path
from textwrap import indent
from typing import Literal, Optional, Set, Tuple, Union

import attrs
from mdutils.tools.TextUtils import TextUtils

from .base import MdObj, RenderedMd, func_kwargs_as_set
from .file import File, store_asset_relpath
from .md_proxy import register_md
from .settings import Settings
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

    def _render(self, javascript_path: Path, page_path: Path, **kwargs) -> RenderedMd:
        # if code-admonition, we need to load additional css
        if self.kind == "code":
            rel_css_path = store_asset_relpath(
                Path("code_admonition.css"),
                javascript_path=javascript_path,
                page_path=page_path,
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
            obj_rendered = self.obj.render(
                **dict(kwargs, javascript_path=javascript_path, page_path=page_path)
            )
            admon_text = obj_rendered.body
            back = obj_rendered.back
            settings = obj_rendered.settings
            settings = cont_settings + settings
        else:
            admon_text, back, settings = str(self.obj), SpacedText(), cont_settings

        if self.title is None:
            title_md = ""
        else:
            title_md = f'"{self.title}"'

        body = SpacedText(
            f"{'???' if self.collapse else '!!!'} {self.kind} {title_md}", (2, 2)
        ) + SpacedText(indent(str(admon_text), "    "), (2, 2))

        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        fixtures = set(["javascript_path", "page_path"])
        if isinstance(self.obj, MdObj):
            fixtures.update(self.obj.render_fixtures())

        return fixtures


@register_md("Tab")
@attrs.mutable
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

    def _render(self, **kwargs) -> RenderedMd:
        tab_settings = Settings(
            mkdocs={
                "markdown_extensions": [
                    "pymdownx.superfences",
                    {"pymdownx.tabbed": {"alternate_style": True}},
                ]
            }
        )
        if isinstance(self.obj, MdObj):
            obj_rendered = self.obj.render(**kwargs)
            tab_text = obj_rendered.body
            back = obj_rendered.back
            settings = obj_rendered.settings
            settings = tab_settings + settings
        else:
            tab_text, back, settings = str(self.obj), SpacedText(), tab_settings

        if self.title is not None:
            title_text = html.escape(self.title)
        else:
            title_text = ""

        body = SpacedText(f'=== "{title_text}"', (2, 2)) + SpacedText(
            indent(str(tab_text), "    "), (2, 2)
        )
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        if isinstance(self.obj, MdObj):
            return self.obj.render_fixtures()
        else:
            return set()


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

    def _render(self) -> RenderedMd:
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
        body = SpacedText(
            TextUtils.insert_code(textwrap.dedent(self.code), annots), (2, 2)
        )
        back = SpacedText("")
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return func_kwargs_as_set(self._render)


@register_md("CodeFile")
class CodeFile(File):
    """
    Code block with the content of a file.
    """

    def __init__(
        self,
        path: Union[Path, str],
        title: Optional[str] = None,
        hl_lines: Optional[Tuple[int, int]] = None,
        language: Optional[str] = "python",
    ):
        """
        Set up the code-block with file content.

        Args:
            path (Union[Path, str]): Abolute path or relative to current working dir for the
                code-file to be included.
            title (Optional[str]): Title of the code-block. If 'None', the path of the
                code file relative to the project root will be added. If it should be
                empty, set to empty string.
            hl_lines (Optional[Tuple[int, int]]): Optional range of lines for highlighting.
            language (Optional[str]): Language for syntax highlighting.
        """
        super().__init__(path=Path(path), allow_copy=True, use_hash=True)
        self.title = title
        self.hl_lines = hl_lines
        self.language = language

    def _render(
        self, project_root: Path, report_path: Path, store_path: Path
    ) -> RenderedMd:
        super().render(store_path=store_path)
        self.title = (
            self.title
            if self.title is not None
            else str(self.path.relative_to(project_root))
        )

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
        body = SpacedText(
            TextUtils.insert_code(
                f"--8<-- '{self.path.relative_to(report_path)}'", annots
            ),
            (2, 2),
        )
        back = SpacedText("")
        settings = settings
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return func_kwargs_as_set(self._render)
