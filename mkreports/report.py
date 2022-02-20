"""
Base class for the whole report.

This corresponds to a mkdocs project. The class is mainly
responsible for creating a mkdocs project if it doesn't exist
already and ensuring that the neccessary settings are all 
included. 
"""
import os
import shutil
from contextlib import nullcontext
from pathlib import Path
from typing import Any, ContextManager, Dict, Mapping, Optional, Tuple, Union

import yaml
from frontmatter.default_handlers import DEFAULT_POST_TEMPLATE, YAMLHandler
from immutabledict import immutabledict

from .code_context import CodeContext, Layouts
from .exceptions import (ContextActiveError, IncorrectSuffixError,
                         ReportExistsError, ReportNotExistsError,
                         ReportNotValidError)
from .md import (IDStore, MdObj, MdProxy, PageInfo, Raw, SpacedText, Text,
                 merge_settings)
from .settings import (NavEntry, add_nav_entry, load_yaml, path_to_nav_entry,
                       save_yaml)
from .utils import find_comment_ids, repo_root

default_settings = immutabledict(
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


def load_page(path: Union[Path, str]) -> Tuple[Dict[str, Any], str]:
    path = Path(path)
    if not path.exists():
        return {}, ""
    with path.open("r") as f:
        text = f.read()

    handler = YAMLHandler()
    try:
        fm, content = handler.split(text)
        metadata = handler.load(fm)
    except:
        metadata = {}
        content = text

    return metadata, content


def write_page(path: Union[Path, str], metadata, content) -> None:
    handler = YAMLHandler()
    metadata = handler.export(metadata)
    start_delimiter = handler.START_DELIMITER
    end_delimiter = handler.END_DELIMITER
    with Path(path).open("w") as f:
        text = DEFAULT_POST_TEMPLATE.format(
            metadata=metadata,
            content=content,
            start_delimiter=start_delimiter,
            end_delimiter=end_delimiter,
        )
        f.write(text)


class Report:
    """Class representing a report."""

    def __init__(
        self,
        path: Optional[Union[str, Path]] = None,
        project_root: Optional[Union[str, Path]] = None,
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
        """
        # need to ensure it is of type Path
        if path is None:
            try:
                path = os.environ["MKREPORTS_DIR"]
            except Exception:
                raise ValueError(
                    "If no report path is given, the 'MKREPORTS_DIR'  environment variable has to be set."
                )
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
    def javascript_path(self) -> Path:
        """
        Returns:
            Path: Location of the javascript folder.

        """
        return self.docs_dir / "javascript"

    @classmethod
    def create(
        cls,
        path: Union[str, Path],
        report_name: str,
        settings: Optional[Mapping[str, str]] = default_settings,
        exist_ok: bool = False,
    ) -> "Report":
        """
        Create a new report.

        Args:
            path (Union[str, Path]): Top-level folder of the report.
            report_name (str): Name of the report (mkdocs site-name)
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

        return cls(path)

    def _add_nav_entry(self, nav_entry) -> None:
        # check that the nav-entry is relative; if absolute,
        # make it relative to the docs_dir
        if isinstance(nav_entry[1], str):
            nav_entry = NavEntry(nav_entry[0], Path(nav_entry[1]))
        if nav_entry[1].is_absolute():
            nav_entry = NavEntry(nav_entry[0], nav_entry[1].relative_to(self.docs_dir))

        mkdocs_settings = load_yaml(self.mkdocs_file)
        mkdocs_settings = add_nav_entry(mkdocs_settings, nav_entry)
        save_yaml(mkdocs_settings, self.mkdocs_file)

    def page(
        self,
        page_name: Union[NavEntry, Path, str],
        truncate: bool = False,
        add_bottom: bool = True,
    ) -> "Page":
        """
        Create a page in the report.

        Args:
            page_name (Union[NavEntry, Path, str]): Name of the page and path. Using a
                **NavEntry**, a custom nav-entry and path can be specified. The path
                is always relative to the report-docs directory.
            truncate (bool): Should the page be truncated if it exists? Also deletes
                the *store_path*.
            add_bottom (bool): Should new entries be added at the bottom or at the
                top of the page. Top of the page is used for IPython.

        Returns:
            Page: An object representing a new page.

        """
        # if the page_name is just a string, we turn it into a dictionary
        # based on the hierarchical names
        if isinstance(page_name, (str, Path)):
            path = Path(page_name)
            if path.suffix == "":
                path = path.with_suffix(".md")
            nav_entry = path_to_nav_entry(path)
        else:
            nav_entry = page_name
            path = nav_entry[1]

        if path.suffix == "":
            path = path.with_suffix(".md")
        if path.suffix != ".md":
            raise ValueError(f"{path} needs to have extension '.md'")

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
        )

        if truncate:
            if page.store_path.exists():
                shutil.rmtree(page.store_path)

        return page


class Page:
    """Represents a single page of report."""

    def __init__(
        self,
        path: Path,
        report: Report,
        code_layout: Layouts = "tabbed",
        code_name_only: bool = False,
        add_bottom: bool = True,
    ) -> None:
        """
        Initialize a page. Usually this is not used and instead a page is created
        using the *page* method on a report.

        A page is also a context manager. If the context manager is active, code
        that is run in it is being tracked and added to the output with the
        specified layouts. The specified layout is used for all code tracking.
        Only one context-manager for a page can be active at a time.

        Args:
            path (Path): Path to the page (absolute or relative to cwd).
            report (Report): The report object to which the page belongs.
            code_layout (Layouts): Type of layout for code-tracking. One of
                'tabbed', 'top-o', 'top-c', 'bottom-o', 'bottom-c' or 'nocode'.
            code_name_only (bool): For code files, should only the name be used
                instead of the path.
            add_bottom (bool): Should new entries be added at the bottom? At the
                top used for IPython.
        """
        self._path = path.absolute()
        # check that the file exists and ends with .md
        if not self.path.exists():
            raise FileNotFoundError(f"file {self.path} does not exist.")
        if not self.path.suffix == ".md":
            raise IncorrectSuffixError(f"file {self.path} does not have suffix '.md'")

        # we need to parse the file for ids
        self._idstore = IDStore(used_ids=find_comment_ids(self.path.read_text()))
        self.report = report
        self.add_bottom = add_bottom
        self.code_layout: Layouts = code_layout
        self.code_name_only = code_name_only

        self._md = MdProxy(page_info=self.page_info)

        self.code_context: Optional[CodeContext] = None

    def __enter__(self) -> "Page":
        if self.code_context is not None and self.code_context.active:
            raise ContextActiveError("The context manager is already active")
        if self.code_context is None:
            self.code_context = CodeContext(
                layout=self.code_layout,
                name_only=self.code_name_only,
                add_bottom=self.add_bottom,
                relative_to=self.report.project_root,
            )
        self.code_context.__enter__()
        return self

    def ctx(
        self,
        layout: Optional[Layouts] = None,
        name_only: Optional[bool] = None,
        add_bottom: Optional[bool] = None,
    ) -> "Page":
        """
        Sets the next context to be used. Only counts for the next tracking context.

        Args:
            layout (Optional[Layouts]): The layout to use. One of
                'tabbed', 'top-o', 'top-c', 'bottom-o', 'bottom-c' or 'nocode'.
            name_only (Optional[bool]): In the code block, should only the name of the
                file be used.
            add_bottom (Optional[bool]): Is new output added to the bottom or top.

        Returns:
            Page: The page object, but with the new *CodeContext* object set.

        """
        if self.code_context is not None and self.code_context.active:
            raise ContextActiveError("The context manager is already active")
        self.code_context = CodeContext(
            layout=layout if layout is not None else self.code_layout,
            name_only=name_only if name_only is not None else self.code_name_only,
            add_bottom=add_bottom if add_bottom is not None else self.add_bottom,
            relative_to=self.report.project_root,
        )
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        if self.code_context is None:
            raise Exception("__exit__ called before __enter__")
        self.code_context.__exit__(exc_type, exc_val, traceback)
        self._add_to_page(self.code_context.md_obj(page_info=self.page_info))
        self.code_context = None

    def __getattr__(self, name):
        md_class = self.md.__getattr__(name)

        def md_and_add(*args, **kwargs):
            kwargs_add = {}
            kwargs_md = kwargs

            # now apply to md
            md_obj = md_class(*args, **kwargs_md)
            return self.add(md_obj, **kwargs_add)

        return md_and_add

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    @property
    def page_info(self):
        """
        Returns:
            PageInfo: An object with info about the page used in markdown objects.
        """
        return PageInfo(
            store_path=self.store_path,
            report_path=self.report.path,
            javascript_path=self.report.javascript_path,
            project_root=self.report.project_root,
            idstore=self._idstore,
            page_path=self.path,
        )

    @property
    def notrack(self) -> ContextManager["Page"]:
        """
        Context-manager that does not do anything.

        This can be useful if a context-manager is used for visual grouping of code
        - e.g. when using the context manager on headings. This context manager
        can be used even if another is already active.

        Returns:
            ContextManager["Page"]: Returns a null context manager that wraps the page.

        """
        return nullcontext(self)

    @property
    def path(self) -> Path:
        """
        Returns:
            Path: Absolute path to the page.

        """
        return self._path

    @property
    def store_path(self) -> Path:
        """
        Returns:
            Path: Location of the path for object storage for the page.

        """
        return self.path.parent / (self._path.stem + "_store")

    def clear(self) -> None:
        """Clear the page markdown file and the generated assets directory."""
        shutil.rmtree(self.store_path)
        self.path.unlink()

    def add(
        self,
        item: Union[MdObj, Text],
    ) -> "Page":
        """
        Add a MdObj to the page.

        Args:
            item (Union[MdObj, Text]): Object to add to the page

        Returns:
            Page: The page itself.

        """
        # first ensure that item is an MdObj
        if isinstance(item, str):
            item = Raw(item, dedent=True)
        elif isinstance(item, SpacedText):
            item = Raw(item)

        # if a context-manager is active, pass along the object into there
        if self.code_context is not None:
            self.code_context.add(item)
        else:  # else pass it directly to the page
            self._add_to_page(item)

        # we return a copy of the page, but with the code context not copied
        # the copy is therefore a shallow copy
        # page_copy = copy.copy(self)
        # page_copy.code_context = None
        return self

    def _add_to_page(
        self,
        item: MdObj,
    ) -> None:
        """
        Read the frontmatter and merge it with the additional settings.

        The reason that we do this separately is a minor issue in the
        frontmatter library, that filters the newlines at the end of the file.
        https://github.com/eyeseast/python-frontmatter/issues/87
        """
        # call the markdown and the backmatter
        md_text = item.body + item.back

        req = item.settings
        if len(req.mkdocs) > 0:
            # merge these things into mkdocs
            # there is not allowed to be a nav here
            if "nav" in req.mkdocs:
                raise ValueError("nav not allowed to be in mkdocs")

            mkdocs_settings = load_yaml(self.report.mkdocs_file)
            mkdocs_settings = merge_settings(mkdocs_settings, req.mkdocs)
            save_yaml(mkdocs_settings, self.report.mkdocs_file)

        metadata, content = load_page(self.path)
        # we need to read the whole page anyway
        metadata = merge_settings(metadata, req.page)

        if self.add_bottom:
            content = content + md_text.format_text(content, "")
        else:
            content = md_text.format_text("", content) + content

        write_page(self.path, metadata, content)

    @property
    def md(self) -> MdProxy:
        """
        A proxy for the 'md' submodule.
        """
        return self._md
