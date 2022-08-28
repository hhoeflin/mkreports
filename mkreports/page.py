import shutil
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from frontmatter.default_handlers import DEFAULT_POST_TEMPLATE, YAMLHandler

from .code_context import CodeContext, Layouts, MultiCodeContext
from .exceptions import IncorrectSuffixError
from .md import IDStore, MdObj, MdProxy, comment, merge_settings
from .settings import NavEntry
from .utils import find_comment_ids


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


def merge_pages(
    path_source: Path, path_target: Path, mode: Literal["S", "T", "ST", "TS"] = "TS"
) -> None:

    if mode == "S":
        shutil.copy(path_source, path_target)
        return
    elif mode == "T":
        # nothing to do
        return

    metadata_source, content_source = load_page(path_source)
    metadata_target, content_target = load_page(path_target)
    if mode == "ST":
        metadata_res = merge_settings(metadata_source, metadata_target)
        content_res = content_source + comment("Merged file boundary") + content_target
    elif mode == "TS":
        metadata_res = merge_settings(metadata_target, metadata_source)
        content_res = content_target + comment("Merged file boundary") + content_source
    else:
        raise ValueError("Unknown mode {mode}")

    write_page(path=path_target, metadata=metadata_res, content=content_res)


class Page(MultiCodeContext):
    """Represents a single page of report."""

    def __init__(
        self,
        path: Path,
        report: "Report",  # type: ignore
        code_layout: Layouts = "tabbed",
        code_name_only: bool = False,
        add_bottom: bool = True,
        md_defaults: Optional[Dict[str, Dict[str, Any]]] = None,
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
            md_defaults (Optional[Dict[str, Dict[str, Any]]): A dictionary mapping the names
                md objects (accessed from the proxy) to default keywords included when
                they are being called.
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

        # initialize the MultiCodeContext
        super().__init__(
            add_no_active_ctx_cb=self._add_to_page,  # on exit, adds to the page
            code_layout=code_layout,
            code_name_only=code_name_only,
            add_bottom=add_bottom,
            relative_to=self.report.project_root,
        )

        self._md = MdProxy(md_defaults=md_defaults)

        self.code_context_stack: List[CodeContext] = []

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
    def fixtures(self):
        """
        Returns:
            dict: A dictionary with the default fixtures for the page.
        """
        return dict(
            page_asset_path=self.asset_path,
            report_asset_path=self.report.asset_path,
            report_path=self.report.path,
            javascript_path=self.report.javascript_path,
            project_root=self.report.project_root,
            idstore=self._idstore,
            page_path=self.path,
        )

    @property
    def path(self) -> Path:
        """
        Returns:
            Path: Absolute path to the page.

        """
        return self._path

    @property
    def nav_entry(self) -> NavEntry:
        """
        Returns:
            NavEntry for this page.

        """
        nav_entry = self.report.get_nav_entry(self.rel_path)

        # the entry cannot be none, or the page would not exist
        assert nav_entry is not None
        return nav_entry

    @property
    def asset_path(self) -> Path:
        """
        Returns:
            Path: Location of the path for object storage for the page.

        """
        return self.path.parent / self._path.stem

    def clear(self) -> None:
        """Clear the page markdown file and the generated assets directory."""
        shutil.rmtree(self.asset_path)
        self.path.unlink()

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
        # first the item needs to be rendered
        item_rendered = item.render(**self.fixtures)

        # call the markdown and the backmatter
        md_text = item_rendered.body + item_rendered.back

        req = item_rendered.settings
        if len(req.mkdocs) > 0:
            # merge these things into mkdocs
            # there is not allowed to be a nav here
            if "nav" in req.mkdocs:
                raise ValueError("nav not allowed to be in settings of markdown item")

            self.report.settings.merge(req.mkdocs)

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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.__dict__ == other.__dict__
