import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from frontmatter.default_handlers import DEFAULT_POST_TEMPLATE, YAMLHandler

from .code_context import CodeContext, Layouts
from .exceptions import IncorrectSuffixError
from .md import (IDStore, MdObj, MdProxy, PageInfo, Raw, SpacedText, Text,
                 merge_settings)
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


class Page:
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
        self.add_bottom = add_bottom
        self.code_layout: Layouts = code_layout
        self.code_name_only = code_name_only

        self._md = MdProxy(page_info=self.page_info, md_defaults=md_defaults)

        self.code_context_stack: List[CodeContext] = []

    def __enter__(self) -> "Page":
        if len(self.code_context_stack) == 0 or (
            len(self.code_context_stack) > 0 and self.code_context_stack[-1].active
        ):
            # need to enter a new context
            self.code_context_stack.append(
                CodeContext(
                    layout=self.code_layout,
                    name_only=self.code_name_only,
                    add_bottom=self.add_bottom,
                    relative_to=self.report.project_root,
                )
            )
        else:
            # use the existing one that is not active yet
            pass
        # the last one on the stack is the one we activate
        self.code_context_stack[-1].__enter__()
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
        new_code_context = CodeContext(
            layout=layout if layout is not None else self.code_layout,
            name_only=name_only if name_only is not None else self.code_name_only,
            add_bottom=add_bottom if add_bottom is not None else self.add_bottom,
            relative_to=self.report.project_root,
        )

        if len(self.code_context_stack) == 0 or (
            len(self.code_context_stack) > 0 and self.code_context_stack[-1].active
        ):
            # need to add new one
            self.code_context_stack.append(new_code_context)
        else:
            # need to replace existing one
            self.code_context_stack[-1] = new_code_context

        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        if len(self.code_context_stack) == 0:
            raise Exception("__exit__ called before __enter__")
        active_code_context = self.code_context_stack.pop()
        active_code_context.__exit__(exc_type, exc_val, traceback)

        # self.add accounts for remaining active code_context
        self.add(active_code_context.md_obj(page_info=self.page_info))

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
    def path(self) -> Path:
        """
        Returns:
            Path: Absolute path to the page.

        """
        return self._path

    @property
    def rel_path(self) -> Path:
        """
        Returns:
            Path: Relative to the docs_dir of the report.

        """
        return self._path.relative_to(self.report.docs_dir)

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

        # search from the top for active code_context
        active_code_context = None
        for i in reversed(range(len(self.code_context_stack))):
            if self.code_context_stack[i].active:
                active_code_context = self.code_context_stack[i]
                break

        # if a context-manager is active, pass along the object into there
        if active_code_context is not None:
            active_code_context.add(item)
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
