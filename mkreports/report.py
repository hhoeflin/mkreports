"""
Base class for the whole report.

This corresponds to a mkdocs project. The class is mainly
responsible for creating a mkdocs project if it doesn't exist
already and ensuring that the neccessary settings are all 
included. 
"""
import contextlib
import os
import shutil
import time
from pathlib import Path
from typing import Any, ContextManager, Dict, Mapping, Optional, Tuple, Union

import yaml
from frontmatter.default_handlers import DEFAULT_POST_TEMPLATE, YAMLHandler
from immutabledict import immutabledict

from .exceptions import (ReportExistsError, ReportNotExistsError,
                         ReportNotValidError, TrackerEmptyError,
                         TrackerIncompleteError)
from .md import IDStore, MdObj, Raw, SpacedText, Tab, Text, merge_settings
from .md_proxy import MdProxy
from .settings import (NavEntry, add_nav_entry, load_yaml, path_to_nav_entry,
                       save_yaml)
from .stack import Tracker
from .utils import relative_repo_root

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
    def __init__(
        self,
        path: Optional[Union[str, Path]] = None,
    ) -> None:
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

    @classmethod
    def create(
        cls,
        path: Union[str, Path],
        report_name: str,
        settings: Optional[Mapping[str, str]] = default_settings,
        exist_ok: bool = False,
    ) -> "Report":
        path = Path(path)
        # create the directory
        (path / "docs").mkdir(exist_ok=exist_ok, parents=True)
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
            nav_entry = (nav_entry[0], Path(nav_entry[1]))
        if nav_entry[1].is_absolute():
            nav_entry = (nav_entry[0], nav_entry[1].relative_to(self.docs_dir))

        mkdocs_settings = load_yaml(self.mkdocs_file)
        mkdocs_settings = add_nav_entry(mkdocs_settings, nav_entry)
        save_yaml(mkdocs_settings, self.mkdocs_file)

    def page(
        self,
        page_name: Union[NavEntry, Path, str],
        truncate: bool = False,
        init_counter_time: bool = False,
        append_code_file: Optional[Union[str, Path]] = None,
    ) -> "Page":
        # if the page_name is just a string, we turn it into a dictionary
        # based on the hierarchical names
        if isinstance(page_name, (str, Path)):
            path = Path(page_name)
            nav_entry = path_to_nav_entry(path)
        else:
            nav_entry = page_name
            path = nav_entry[1]

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

        return Page(
            self.docs_dir / path,
            report=self,
            init_counter_time=init_counter_time,
            append_code_file=append_code_file,
        )


class Page:
    def __init__(
        self,
        path: Path,
        report: Report,
        init_counter_time: bool = False,
        append_code_file: Optional[Union[Path, str]] = None,
    ) -> None:
        self._path = path.absolute()
        if init_counter_time:
            # use time in ms
            self._idstore = IDStore(start_with=int(time.time() * 1000))
        else:
            self._idstore = IDStore()
        self.report = report

        self._md = MdProxy(
            store_path=self.gen_asset_path,
            report_path=self.report.path,
        )

        self.append_code_file = append_code_file

        # a tracker for tracking code to be printed
        self.reset_tracker()

    def __enter__(self) -> "Page":
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        del exc_type, exc_val, traceback
        if self.append_code_file:
            try:
                self.add(
                    self.md.Admonition(
                        self.md.CodeFile(self.append_code_file),
                        collapse=True,
                        kind="info",
                        title=relative_repo_root(self.append_code_file),
                    )
                )
            except Exception:
                pass

    def __getattr__(self, name):
        md_class = self.md.__getattr__(name)

        def md_and_add(*args, **kwargs):
            kwargs_add = {
                name: value
                for name, value in kwargs.items()
                if name in ["add_code", "bottom"]
            }
            kwargs_md = {
                name: value
                for name, value in kwargs.items()
                if name not in ["add_code", "bottom"]
            }

            # now apply to md
            md_obj = md_class(*args, **kwargs_md)
            return self.add(md_obj, **kwargs_add)

        return md_and_add

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

    def reset_tracker(self) -> None:
        # note: tracker is designed to be passed outside
        self.tracker = Tracker(omit_levels=0)

    def track_code(self):
        self.reset_tracker()
        return self.tracker

    def track_code_start(self):
        self.tracker.__enter__()

    def track_code_end(self):
        self.tracker.__exit__(None, None, None)

    def md_code(self, highlight: bool = True, full_filename: bool = False) -> MdObj:
        """Print code as markdown that has been tracked."""
        if self.tracker.ctx_active:
            raise TrackerIncompleteError("The tracker has not finished.")
        if self.tracker.tree is None:
            raise TrackerEmptyError("The tracker has not been started.")
        return self.tracker.tree.md_tree(
            highlight=highlight, full_filename=full_filename
        )

    def add(
        self, item: Union[MdObj, Text], add_code: bool = False, bottom: bool = True
    ) -> ContextManager["Page"]:
        # first ensure that item is an MdObj
        if isinstance(item, str):
            item = Raw(item, dedent=True)
        elif isinstance(item, SpacedText):
            item = Raw(item)

        if add_code:
            # we wrap it all in a tabs, with one tab the main output, the other
            # the code;
            item = Tab(item, title="Content") + Tab(
                self.md_code(highlight=False), title="Code"
            )
            # reset the tracker
            self.reset_tracker()

        # call the markdown and the backmatter
        md_out = item.to_markdown(page_path=self.path, idstore=self._idstore)
        md_text = md_out.body + md_out.back

        req = item.req_settings()
        if len(req.mkdocs) > 0:
            # merge these things into mkdocs
            # there is not allowed to be a nav here
            if "nav" in req.mkdocs:
                raise ValueError("nav not allowed to be in mkdocs")

            mkdocs_settings = load_yaml(self.report.mkdocs_file)
            mkdocs_settings = merge_settings(mkdocs_settings, req.mkdocs)
            save_yaml(mkdocs_settings, self.report.mkdocs_file)

        if bottom:
            self._add_to_page(top=None, bottom=md_text, page_settings=req.page)
        else:
            self._add_to_page(top=md_text, bottom=None, page_settings=req.page)

        return contextlib.nullcontext(self)

    def _add_to_page(
        self,
        top: Optional[SpacedText],
        bottom: Optional[SpacedText],
        page_settings: Dict[str, Any],
    ) -> None:
        """
        Read the frontmatter and merge it with the additional settings.

        The reason that we do this separately is a minor issue in the
        frontmatter library, that filters the newlines at the end of the file.
        https://github.com/eyeseast/python-frontmatter/issues/87
        """
        metadata, content = load_page(self.path)
        # we need to read the whole page anyway
        metadata = merge_settings(metadata, page_settings)

        if top is not None:
            content = top.format_text("", content) + content
        if bottom is not None:
            content = content + bottom.format_text(content, "")

        write_page(self.path, metadata, content)

    @property
    def md(self) -> MdProxy:
        """
        A proxy for the 'md' submodule that specifies 'store_path' where possible.
        """
        return self._md
