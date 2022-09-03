"""
Base class for the whole report.

This corresponds to a mkdocs project. The class is mainly
responsible for creating a mkdocs project if it doesn't exist
already and ensuring that the neccessary settings are all 
included. 
"""
import shutil
from pathlib import Path
from typing import Any, Dict, Literal, Mapping, Optional, Union

import yaml
from immutabledict import immutabledict

from .config import get_mkreports_dir
from .exceptions import ReportExistsError, ReportNotExistsError, ReportNotValidError
from .page import Page, merge_pages
from .settings import NavEntry, ReportSettings, path_to_nav_entry
from .utils import repo_root

default_settings: Any = immutabledict(
    {
        "theme": {
            "name": "material",
            "custom_dir": "overrides",
        },
        "nav": [{"Home": "index.md"}],
        "markdown_extensions": [
            "meta",
            "admonition",
            "pymdownx.extra",
            "pymdownx.details",
            "pymdownx.superfences",
        ],
    }
)

# template
main_html_override = """
{% extends "base.html" %}

{% block extrahead %}

  {% if page and page.meta and page.meta.css %}
    {% for css_load in page.meta.css %}
        <link rel="stylesheet" href="{{css_load}}">
    {% endfor %}

  {% endif %}

  {% if page and page.meta and page.meta.javascript %}

    {% for js_load in page.meta.javascript %}
        <script type="text/javascript" src="{{js_load}}"></script>
    {% endfor %}

  {% endif %}
{% endblock %}
"""


def normalize_nav_entry(nav_entry: Union[str, Path, NavEntry]) -> NavEntry:
    """
    Normalize a nav entry

    Ensures that if a string or Path is given, is turned into a NavEntry.

    Args:
        nav_entry (Union[str, Path, NavEntry]): The str, path or nav_entry to use.

    Returns:

    """
    if isinstance(nav_entry, (str, Path)):
        path = Path(nav_entry)
        if path.suffix == "":
            path = path.with_suffix(".md")
        nav_entry = path_to_nav_entry(path)
    else:
        path = Path(nav_entry.loc)

    if path.suffix != ".md":
        raise ValueError(f"{path} needs to have extension '.md'")

    return nav_entry


class Report:
    """Class representing a report."""

    def __init__(
        self,
        path: Optional[Union[str, Path]] = None,
        project_root: Optional[Union[str, Path]] = None,
        md_defaults: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        """
        Initialize the report object. This relies on the report folder already
        existing, including necessary files for mkdocs. If this is not the case,
        use the **create** class-method.

        Args:
            path (Optional[Union[str, Path]]): Path to the top-level directory of the report.
            project_root (Optional[Union[str, Path]]):
                Directory that is the root of the project. If None, tries to use
                the root of the git-repository if there is one. Otherwise
                uses the root of the file-system.
            md_defaults (Optional[Dict[str, Dict[str, Any]]): A dictionary mapping the names
                md objects (accessed from the proxy) to default keywords included when
                they are being called.
        """
        # need to ensure it is of type Path
        if path is None:
            path = get_mkreports_dir()

        self._path = Path(path).absolute()
        # first check if the path exists and is not empty and return error if that is not ok
        if not self.path.exists():
            raise ReportNotExistsError(f"{self.path} does not exist.")
        if not self.mkdocs_file.exists() or not self.mkdocs_file.is_file():
            raise ReportNotValidError(f"{self.mkdocs_file} does not exist")
        if not self.docs_dir.exists() or not self.docs_dir.is_dir():
            raise ReportNotValidError(f"{self.docs_dir} does not exist")
        if not self.index_file.exists() or not self.index_file.is_file():
            raise ReportNotValidError(f"{self.index_file} does not exist")

        if project_root is None:
            root = repo_root()
            if root is None:
                self.project_root = Path("/")
            else:
                self.project_root = root
        else:
            self.project_root = Path(project_root)

        self.md_defaults = md_defaults

    @property
    def path(self) -> Path:
        """
        Returns:
            Path: Path object that is the top-level of the report.
        """
        return self._path

    @property
    def mkdocs_file(self) -> Path:
        """
        Returns:
            Path: Location of the mkdocs file.

        """
        return self.path / "mkdocs.yml"

    @property
    def docs_dir(self) -> Path:
        """
        Returns:
            Path: Docs-folder in the report.

        """
        return self.path / "docs"

    @property
    def index_file(self) -> Path:
        """
        Returns:
            Path: Location of the index file.

        """
        return self.docs_dir / "index.md"

    @property
    def asset_dir(self):
        """
        Returns:
            The asset path for the report.
        """
        return self.docs_dir / "assets"

    @property
    def settings(self):
        return ReportSettings(self.mkdocs_file)

    @classmethod
    def create(
        cls,
        path: Union[str, Path],
        report_name: str,
        project_root: Optional[Union[str, Path]] = None,
        md_defaults: Optional[Dict[str, Dict[str, Any]]] = None,
        settings: Optional[Mapping[str, str]] = default_settings,
        exist_ok: bool = False,
    ) -> "Report":
        """
        Create a new report.

        Args:
            path (Union[str, Path]): Top-level folder of the report.
            report_name (str): Name of the report (mkdocs site-name)
            project_root (Optional[Union[str, Path]]):
                Directory that is the root of the project. If None, tries to use
                the root of the git-repository if there is one. Otherwise
                uses the root of the file-system.
            md_defaults (Optional[Dict[str, Dict[str, Any]]): A dictionary mapping the names
                md objects (accessed from the proxy) to default keywords included when
                they are being called.
            settings (Optional[Mapping[str, str]]): Settings of the report.
            exist_ok (bool): Is it ok if it already exists?

        Returns:
            Report: An instance of the class representing the project.

        """
        path = Path(path)
        # create the directory
        try:
            (path / "docs").mkdir(exist_ok=exist_ok, parents=True)
        except FileExistsError:
            raise ReportExistsError(f"{path / 'docs'} already exists.")

        # index.md created, but done nothing if it exists
        # if exist_ok=False, the previousalready failed otherwise
        (path / "docs" / "index.md").touch()

        # only do it if mkdocs_yml does not exist yet
        mkdocs_file = path / "mkdocs.yml"
        if not mkdocs_file.exists():
            # the settings are our serialized yaml
            # ensure settings is regular dict
            settings = dict(settings.items()) if settings is not None else {}
            settings["site_name"] = report_name
            with (path / "mkdocs.yml").open("w") as f:
                yaml.dump(settings, f, Dumper=yaml.Dumper, default_flow_style=False)

        # also create the overrides doc
        overrides_dir = path / "overrides"
        overrides_dir.mkdir(exist_ok=True, parents=True)
        with (overrides_dir / "main.html").open("w") as f:
            f.write(main_html_override)

        return cls(
            path,
            project_root=project_root,
            md_defaults=md_defaults,
        )

    def _add_nav_entry(self, nav_entry) -> None:
        # check that the nav-entry is relative; if absolute,
        # make it relative to the docs_dir
        loc = nav_entry.loc
        if isinstance(loc, str):
            loc = Path(loc)
        if loc.is_absolute():  # type: ignore
            loc = loc.relative_to(self.docs_dir)

        self.settings.append_nav_entry(NavEntry(nav_entry.hierarchy, loc))

    def get_nav_entry(self, path: Path) -> Optional[NavEntry]:
        """
        Get the NavEntry for a specific page.

        Args:
            path (Path): Path to the page, absolute or relative to docs_dir.

        Returns:
            The NavEntry if it exists or None.

        """
        if path.is_absolute():
            rel_path = path.relative_to(self.docs_dir)
        else:
            rel_path = path

        nav_list = self.settings.nav_list

        match_entries = [
            nav_entry for nav_entry in nav_list if nav_entry.loc == rel_path
        ]

        if len(match_entries) > 0:
            return match_entries[0]
        else:
            return None

    def page(
        self,
        page_name: Union[NavEntry, Path, str],
        truncate: bool = False,
        add_bottom: bool = True,
        md_defaults: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> "Page":
        """
        Create a page in the report.

        Args:
            page_name (Union[NavEntry, Path, str]): Name of the page and path. Using a
                **NavEntry**, a custom nav-entry and path can be specified. The path
                is always relative to the report-docs directory.
            truncate (bool): Should the page be truncated if it exists? Also deletes
                the *asset_dir*.
            add_bottom (bool): Should new entries be added at the bottom or at the
                top of the page. Top of the page is used for IPython.
            md_defaults (Optional[Dict[str, Dict[str, Any]]): A dictionary mapping the names
                md objects (accessed from the proxy) to default keywords included when
                they are being called.

        Returns:
            Page: An object representing a new page.

        """

        nav_entry = normalize_nav_entry(page_name)
        path = nav_entry.loc
        assert isinstance(path, Path)

        # if the file already exists, just return a 'Page',
        # else create a new nav-entry and the file and return a 'Page'
        if (self.docs_dir / path).exists():
            if truncate:
                # delete the existing site
                (self.docs_dir / path).unlink()
                (self.docs_dir / path).touch()
                # we do not need to add en entry into the nav
        else:
            # create the file by touching it and create a nav-entry
            (self.docs_dir / path).parent.mkdir(exist_ok=True, parents=True)
            (self.docs_dir / path).touch()

            # update the report settings
            self._add_nav_entry(nav_entry)

        page = Page(
            self.docs_dir / path,
            report=self,
            add_bottom=add_bottom,
            md_defaults=md_defaults,
        )

        if truncate:
            if page.asset_dir.exists():
                shutil.rmtree(page.asset_dir)

        return page

    def insert_page(
        self,
        path_target: Union[str, Path, NavEntry],
        path_source: Path,
        mode: Literal["S", "T", "ST", "TS"] = "TS",
    ):
        """
        Insert a page into the report.

        This function can take an existing page (can also just be a markdown
            file) and inserts it into the page.

        Args:
            path_source (Path): The file to insert. Expected to be a markdown file.
            path_target (Union[Path, NavEntry]): Path or NavEntry where the page should be
                inserted.
            mode (Literal["S", "T", "ST", "TS"]): Insertion mode. If 'S', then only
                the target is overwritten with the source. If 'T', then the
                target is left as is, if it exists. For 'ST', the source is prepended,
                for 'TS', the source is appended to the target.
        """
        nav_entry = normalize_nav_entry(path_target)
        assert isinstance(nav_entry.loc, Path)

        if mode == "T" and not nav_entry.loc.exists():
            # force source being used
            mode = "S"

        target_page = self.page(path_target)  # initiating entries into the nav

        merge_pages(path_source=path_source, path_target=target_page.path, mode=mode)

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.__dict__ == other.__dict__
