"""
Base class for the whole report.

This corresponds to a mkdocs project. The class is mainly
responsible for creating a mkdocs project if it doesn't exist
already and ensuring that the neccessary settings are all 
included. 
"""
import shutil
from pathlib import Path
from typing import Mapping, Optional, Union

import yaml
from immutabledict import immutabledict

from .counters import Counters
from .exceptions import (ReportExistsError, ReportNotExistsError,
                         ReportNotValidError)
from .md import MdObj, SpacedText, Text
from .requirements import NavEntry, Requirements, path_to_nav_entry

default_settings = immutabledict(
    {
        "theme": {"name": "material"},
        "nav": [{"Home": "index.md"}],
        "markdown_extensions": [
            "admonition",
            "pymdownx.details",
            "pymdownx.superfences",
        ],
    }
)


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
            req = Requirements.load(self.path)
            req.add_nav_entry(nav_entry)
            req.save(self.path)

        return Page(self.docs_dir / path, report=self)

    def update_settings(self, _override=False, **kwargs) -> None:
        update_mkdocs_settings(self.mkdocs_file, _override=_override, **kwargs)


class Page:
    def __init__(self, path: Path, report: Report) -> None:
        self._path = path.absolute()
        self._counters = Counters()
        self.report = report

        # get the last string that was written into the page (if it exists)
        # otherwise we set it to newlines.
        if self.path.exists():
            with self.path.open("r") as f:
                last_lines = f.readlines()[-3:]
            self._last_obj = SpacedText("".join(last_lines))
        else:
            self._last_obj = SpacedText("\n\n\n")

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

    def append(self, item: Union[MdObj, Text]) -> None:
        if isinstance(item, MdObj):
            md_text = item.to_md_with_bm(
                page_path=self.path,
            )
            req = item.requirements()
            if len(req.mkdocs) + len(req.mkreports) > 0:
                self.report.update_settings(req)
        elif isinstance(item, (str, SpacedText)):
            md_text = SpacedText(item)
        else:
            raise Exception("item should be a str, SpacedText or MdObj")

        with self.path.open("a") as f:
            f.write(last_obj := md_text.format_text(self._last_obj, "a"))
        self._last_obj = last_obj
