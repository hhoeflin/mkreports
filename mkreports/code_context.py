"""
Module providing a class and context manager for tracking code.

The way of tracking code and displaying it is handled
through a context manager, which is the return value
obtained when adding an object to a page.

The context manager gives different options on how 
to display the code and the results such as:

- A code block at the top followed by the output similar to 
  standard jupyter notebooks.
- A Tab-format where output and code are on separate tabs
- A collapsed code block followed by the output or the output
  followed by a collapsed code block.
"""
import inspect
from pathlib import Path
from typing import Literal, Optional

from .md import Admonition, HLine, MdObj, MdSeq, PageInfo, Tab
from .tracker import BaseTracker, SimpleTracker

Layouts = Literal["top-c", "top-o", "bottom-c", "bottom-o", "tabbed", "nocode"]


def do_layout(
    code: Optional[MdObj], content: MdObj, layout: Layouts, page_info: PageInfo
) -> MdObj:
    """
    Do the layouting for a content and code block.

    Args:
        code (Optional[MdObj]): The MdObj for the code. If layout is 'nocode', can be None.
        content (MdObj): The content to add. Can't be missing.
        layout (Layouts): Type of layout for code-tracking. One of
                'tabbed', 'top-o', 'top-c', 'bottom-o', 'bottom-c' or 'nocode'.
        page_info (PageInfo): PageInfo object corresponding to the page to which it
            should be added.

    Returns:
        A MdObj with the requested layout.

    """
    if layout == "nocode":
        return content
    else:
        assert code is not None
        if layout == "top-c":
            return (
                Admonition(
                    code,
                    page_info=page_info,
                    collapse=True,
                    title="Code",
                    kind="code",
                )
                + content
                + HLine()
            )
        elif layout == "top-o":
            return code + content + HLine()
        elif layout == "bottom-c":
            return (
                content
                + Admonition(
                    code,
                    page_info=page_info,
                    collapse=True,
                    title="Code",
                    kind="code",
                )
                + HLine()
            )
        elif layout == "bottom-o":
            return content + code + HLine()
        elif layout == "tabbed":
            return Tab(content, title="Content") + Tab(code, title="Code") + HLine()
        else:
            raise Exception("Unknown layout type.")


class CodeContext:
    """
    Context manager for the code tracking and content accumulation.
    """

    tracker: BaseTracker

    def __init__(
        self,
        layout: Layouts,
        relative_to: Optional[Path] = None,
        name_only: bool = False,
        add_bottom: bool = True,
        stack_level: int = 2,
    ):
        """
        Initialize the context manager. This should usually not be needed by
        end users.

        Args:
            layout (Layouts): The layout to use. One of
                'tabbed', 'top-o', 'top-c', 'bottom-o', 'bottom-c' or 'nocode'.
            relative_to (Optional[Path]): Path relative to where the code file will be named.
            name_only (bool): For the code file, use name instead of path?
            add_bottom (bool): Should content be added to bottom or top of page?
            stack_level (int): Levels lower in the stack where the code is to be tracked.
        """
        self.layout: Layouts = layout
        self.do_tracking = layout != "nocode"
        self.tracker = SimpleTracker()
        self.stack_level = stack_level
        self.obj_list = []
        self.relative_to = relative_to
        self.add_bottom = add_bottom
        self.name_only = name_only

    def __enter__(self) -> "CodeContext":
        if self.do_tracking:
            self.tracker.start(inspect.stack()[self.stack_level])
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        del exc_type, exc_val, traceback
        if self.do_tracking:
            self.tracker.stop(inspect.stack()[self.stack_level])

    @property
    def active(self):
        """Indicates if the tracker is active."""
        return self.tracker.active

    def add(self, md_obj: MdObj) -> None:
        """
        Add a new content object.

        Args:
            md_obj (MdObj): The content to be added.
        """
        if self.add_bottom:
            self.obj_list.append(md_obj)
        else:
            self.obj_list.insert(0, md_obj)

    def md_obj(self, page_info: PageInfo) -> MdObj:
        """
        Return the markdown object that represents output and code.

        Args:
            page_info (PageInfo): PageInfo object about the page where the
                content is to be added.

        Returns:
            MdObj: Markdown object representing the formatted output in the
                requested layout
        """
        content = MdSeq(self.obj_list)
        if self.layout == "nocode":
            code_final = None
        else:
            code_blocks = self.tracker.code()
            # turn code blocks into md
            code_md_list = [
                block.md_code(relative_to=self.relative_to, name_only=self.name_only)
                for block in code_blocks
            ]
            if len(code_md_list) > 1:
                # turn it into tabs
                code_final = Tab(code_md_list[0], title="<main>")
                for block, md_code in zip(code_blocks, code_md_list):
                    code_final += Tab(md_code, title=block.co_name)
            else:
                # just keep the code block as is
                code_final = code_md_list[0]

        return do_layout(
            code=code_final, content=content, page_info=page_info, layout=self.layout
        )
