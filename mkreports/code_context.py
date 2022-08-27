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
from typing import Callable, List, Literal, Optional, Union

import attrs
from typing_extensions import Self

from .md import Admonition, HLine, MdObj, MdSeq, Tab, Text, ensure_md_obj
from .tracker import BaseTracker, SimpleTracker

Layouts = Literal["top-c", "top-o", "bottom-c", "bottom-o", "tabbed", "nocode"]


def do_layout(
    code: Optional[MdObj],
    content: MdObj,
    layout: Layouts,
) -> MdObj:
    """
    Do the layouting for a content and code block.

    Args:
        code (Optional[MdObj]): The MdObj for the code. If layout is 'nocode', can be None.
        content (MdObj): The content to add. Can't be missing.
        layout (Layouts): Type of layout for code-tracking. One of
                'tabbed', 'top-o', 'top-c', 'bottom-o', 'bottom-c' or 'nocode'.

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
        self._active = False

    def __enter__(self) -> "CodeContext":
        if self.do_tracking:
            self.tracker.start(inspect.stack()[self.stack_level])
        self._active = True
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        del exc_type, exc_val, traceback
        self._active = False
        if self.do_tracking:
            self.tracker.stop(inspect.stack()[self.stack_level])

    @property
    def active(self):
        """Indicates if the context-manager is active."""
        return self._active

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

    @property
    def md_obj(self) -> MdObj:
        """
        Return the markdown object that represents output and code.

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

        return do_layout(code=code_final, content=content, layout=self.layout)


@attrs.mutable()
class MultiCodeContext:
    add_no_active_ctx_cb: Callable[[MdObj], None]
    code_layout: Layouts = "tabbed"
    code_name_only: bool = False
    add_bottom: bool = True
    relative_to: Optional[Path] = None
    code_context_stack: List[CodeContext] = attrs.field(default=[], init=False)

    def __enter__(self) -> Self:
        if len(self.code_context_stack) == 0 or (
            len(self.code_context_stack) > 0 and self.code_context_stack[-1].active
        ):
            # need to enter a new context
            self.code_context_stack.append(
                CodeContext(
                    layout=self.code_layout,
                    name_only=self.code_name_only,
                    add_bottom=self.add_bottom,
                    relative_to=self.relative_to,
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
    ) -> Self:
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
            relative_to=self.relative_to,
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

        if len(self.code_context_stack) > 0:
            self.code_context_stack[-1].add(active_code_context.md_obj)
        else:
            self.add_no_active_ctx_cb(active_code_context.md_obj)

    def add(
        self,
        item: Union[MdObj, Text],
    ) -> "Self":
        """
        Add a MdObj to the page.

        Args:
            item (Union[MdObj, Text]): Object to add to the page

        Returns:
            Page: The page itself.

        """
        item = ensure_md_obj(item)
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
            self.add_no_active_ctx_cb(item)

        return self
