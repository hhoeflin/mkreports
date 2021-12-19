"""
Base class for the whole report.

This corresponds to a mkdocs project. The class is mainly
responsible for creating a mkdocs project if it doesn't exist
already and ensuring that the neccessary settings are all 
included. 
"""
import inspect
import shutil
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

import frontmatter
import yaml
from immutabledict import immutabledict

from .counters import Counters
from .exceptions import (ReportExistsError, ReportNotExistsError,
                         ReportNotValidError)
from .md import (MdObj, SpacedText, Text, get_default_store_path,
                 set_default_store_path)
from .settings import (NavEntry, add_nav_entry, load_yaml, merge_settings,
                       path_to_nav_entry, save_yaml)
from .stack import Stack, StackDiff, get_stack, stack_to_tabs

default_settings = immutabledict(
    {
        "theme": {
            "name": "material",
            "custom_dir": "overrides",
            "features": ["toc.integrate"],
        },
        "nav": [{"Home": "index.md"}],
        "markdown_extensions": [
            "meta",
            "admonition",
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


class Report:
    def __init__(
        self,
        path: Union[str, Path],
        site_name: str,
        create: bool = True,
        exist_ok: bool = True,
        settings: Optional[Mapping[str, str]] = None,
    ) -> None:
        # need to ensure it is of type Path
        self._path = Path(path).absolute()
        self.site_name = site_name
        # first check if the path exists and return error if that is not ok
        if self.path.exists():
            if not exist_ok:
                raise ReportExistsError(f"{self.path} already exists")
            else:
                # nothing to do here
                pass
        else:
            # check if should be created
            if create:
                # call the functions from mkdocs that creates a new report
                if settings is None:
                    settings = default_settings
                self._create_new(settings)
            else:
                raise ReportNotExistsError(f"{self.path} does not exist.")

        # ensure that all the dependencies are there
        self._ensure_is_report()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def mkdocs_file(self) -> Path:
        return self.path / "mkdocs.yml"

    @property
    def docs_dir(self) -> Path:
        return self.path / "docs"

    @property
    def index_file(self) -> Path:
        return self.docs_dir / "index.md"

    def _create_new(self, settings: Mapping[str, str]) -> None:
        # create the directories
        self.docs_dir.mkdir(exist_ok=True, parents=True)
        # index.md just remains empty
        self.index_file.touch()
        # the settings are our serialized yaml
        settings = dict(settings.items())  # ensure settings is regular dict
        settings["site_name"] = self.site_name
        with self.mkdocs_file.open("w") as f:
            yaml.dump(settings, f, Dumper=yaml.Dumper, default_flow_style=False)

        # also create the overrides doc
        overrides_dir = self.path / "overrides"
        overrides_dir.mkdir(exist_ok=True, parents=True)
        with (overrides_dir / "main.html").open("w") as f:
            f.write(main_html_override)

    def _ensure_is_report(self) -> None:
        # now ensure that these all exist
        if not self.mkdocs_file.exists() or not self.mkdocs_file.is_file():
            raise ReportNotValidError(f"{self.mkdocs_file} does not exist")
        if not self.docs_dir.exists() or not self.docs_dir.is_dir():
            raise ReportNotValidError(f"{self.docs_dir} does not exist")
        if not self.index_file.exists() or not self.index_file.is_file():
            raise ReportNotValidError(f"{self.index_file} does not exist")

    def get_page(
        self, page_name: Union[NavEntry, Path, str], append: bool = True
    ) -> "Page":
        # if the page_name is just a string, we turn it into a dictionary
        # based on the hierarchical names
        if isinstance(page_name, (str, Path)):
            path = Path(page_name)
            nav_entry = path_to_nav_entry(path)
        else:
            nav_entry = page_name
            path = nav_entry[1]

        # if the file already exists, just return a 'Page',
        # else create a new nav-entry and the file and return a 'Page'
        if (self.docs_dir / path).exists():
            if not append:
                # delete the existing site
                (self.docs_dir / path).unlink()
                (self.docs_dir / path).touch()
                # we do not need to add en entry into the nav
        else:
            # create the file by touching it and create a nav-entry
            (self.docs_dir / path).parent.mkdir(exist_ok=True, parents=True)
            (self.docs_dir / path).touch()

            # update the report settings
            mkdocs_settings = load_yaml(self.mkdocs_file)
            mkdocs_settings = add_nav_entry(mkdocs_settings, nav_entry)
            save_yaml(mkdocs_settings, self.mkdocs_file)

        return Page(self.docs_dir / path, report=self)


def merge_frontmatter(page_path: Path, page_settings: Dict[str, Any]) -> None:
    """
    Read the frontmatter and merge it with the additional settings.

    The reason that we do this separately is a minor issue in the
    frontmatter library, that filters the newlines at the end of the file.
    https://github.com/eyeseast/python-frontmatter/issues/87
    """
    # first load the page; we do this ourselves so that we have
    # the newlines at the end
    with page_path.open("r") as f:
        page_str = f.read()

    # get number of newlines
    num_char_stripped = len(page_str) - len(page_str.rstrip())
    end_chars = page_str[-num_char_stripped:]

    page_post = frontmatter.loads(page_str)
    page_post.metadata = merge_settings(page_post.metadata, page_settings)
    page_out = frontmatter.dumps(page_post) + end_chars

    with page_path.open("w") as f:
        f.write(page_out)


class Page:
    def __init__(self, path: Path, report: Report) -> None:
        self._path = path.absolute()
        self._counters = Counters()
        self.report = report
        self.code_marker_first: Optional[Stack] = None
        self.code_marker_second: Optional[Stack] = None

        # get the last string that was written into the page (if it exists)
        # otherwise we set it to newlines.
        if self.path.exists():
            with self.path.open("r") as f:
                last_lines = f.readlines()[-3:]
            self._last_obj = SpacedText("".join(last_lines))
        else:
            self._last_obj = SpacedText("\n\n\n")
        # set the marker to where it was created
        self.set_marker(omit_levels=1)

    def __enter__(self) -> "Page":
        """Enter context manager and set the default store path."""
        self._old_store_path = get_default_store_path()
        set_default_store_path(self.gen_asset_path)

        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        """Remove the default store path and restore the previous one."""
        set_default_store_path(self._old_store_path)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def gen_asset_path(self) -> Path:
        return self.path.parent / (self._path.stem + "_gen_assets")

    def clear(self) -> None:
        """Clear the page markdown file and the generated assets directory."""
        shutil.rmtree(self.gen_asset_path)
        self.path.unlink()

    def set_marker(self, omit_levels=0):
        self.code_marker_first = self.code_marker_second
        self.code_marker_second = get_stack(omit_levels=omit_levels + 1)

    def md_stack(self, code_range: bool = True, highlight: bool = True) -> MdObj:
        """Stack between 2 markers as markdown."""
        if self.code_marker_first is not None and self.code_marker_second is not None:
            stack_diff = StackDiff(self.code_marker_first, self.code_marker_second)
            return stack_to_tabs(
                stack_diff.changed, code_range=code_range, highlight=highlight
            )
        else:
            raise Exception("Need 2 markers to give a stack difference")

    def add(self, item: Union[MdObj, Text], add_code=True, mark=True) -> None:
        if add_code:
            self.set_marker(omit_levels=1)

        if isinstance(item, MdObj):
            md_text = item.to_md_with_bm(
                page_path=self.path,
            )
            req = item.req_settings()
            if len(req.mkdocs) > 0:
                # merge these things into mkdocs
                # there is not allowed to be a nav here
                if "nav" in req.mkdocs:
                    raise ValueError("nav not allowed to be in mkdocs")

                mkdocs_settings = load_yaml(self.report.mkdocs_file)
                mkdocs_settings = merge_settings(mkdocs_settings, req.mkdocs)
                save_yaml(mkdocs_settings, self.report.mkdocs_file)
            if len(req.page) > 0:
                # frontmatter loads the entire post including frontmatter
                # then we can change it as necessary and write it back
                # as we have to change content at the front, does not work more efficiently
                merge_frontmatter(self.path, req.page)

        elif isinstance(item, str):
            md_text = SpacedText(inspect.cleandoc(item))
        elif isinstance(item, SpacedText):
            md_text = item
        else:
            raise Exception("item should be a str, SpacedText or MdObj")

        with self.path.open("a") as f:
            f.write(last_obj := md_text.format_text(self._last_obj, "a"))
        self._last_obj = last_obj
