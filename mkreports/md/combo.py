from pathlib import Path
from typing import Set, Union

from .base import MdObj, Raw, RenderedMd, func_kwargs_as_set
from .containers import Admonition, CodeFile
from .md_proxy import register_md
from .text import SpacedText


@register_md("HLine")
class HLine(Raw):
    """MdObj making a horizontal line."""

    def __init__(self):
        """Initialize the object."""
        super().__init__(SpacedText("---", (2, 2)))


@register_md("CollapsedCodeFile")
class CollapsedCodeFile(MdObj):
    """A code-file in a collapsed admonition."""

    def __init__(self, file: Union[Path, str], title: str = "Code") -> None:
        """
        Initialize the object.

        Args:
            file (Path): The file path (absolute or reltive to cwd) of the code-file.
            title (str): Title on the admonition that is visible.
        """
        file = Path(file)
        self.obj = Admonition(
            CodeFile(
                file,
                title=None,
            ),
            collapse=True,
            title=title,
            kind="code",
        )

    def _render(
        self,
        report_asset_dir: Path,
        page_path: Path,
        page_asset_dir: Path,
        project_root: Path,
        report_path: Path,
    ) -> RenderedMd:
        obj_rendered = self.obj.render(
            report_asset_dir=report_asset_dir,
            page_path=page_path,
            page_asset_dir=page_asset_dir,
            project_root=project_root,
            report_path=report_path,
        )
        return obj_rendered

    def render_fixtures(self) -> Set[str]:
        return func_kwargs_as_set(self._render)


@register_md("HideToc")
class HideToc(Raw):
    """
    Hide the ToC on the page.

    Once added to a page, this can't be reversed.
    """

    def __init__(self):
        """Initialize the object."""
        super().__init__(page_settings=dict(hide=["toc"]))


@register_md("HideNav")
class HideNav(Raw):
    """
    Hide the Nav-bar on the page.

    Once added to a page, this can't be reversed. When the nav-bar is hidden,
    it can be hard to navigate. Consider added 'NavTabs', that show a header
    of navigation tabs. Please note that 'HideNav' affects only the current page,
    while adding NavTabs affects the entire report.
    """

    def __init__(self):
        """Initialize the object."""
        super().__init__(page_settings=dict(hide=["navigation"]))


@register_md("NavTabs")
class NavTabs(Raw):
    """
    Add a header with navigation tabs.

    This cannot be reversed once added. Affects the entire report.
    """

    def __init__(self):
        """Initialize the object."""
        super().__init__(mkdocs_settings={"theme": {"features": ["navigation.tabs"]}})
