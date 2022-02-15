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

from .md import Admonition, HLine, MdObj, MdSeq, Raw, SpacedText, Tab
from .tracker import BaseTracker, SimpleTracker

Layouts = Literal["top-c", "top-o", "bottom-c", "bottom-o", "tabbed", "nocode"]


class CodeContext:
    tracker: BaseTracker

    def __init__(
        self,
        layout: Layouts,
        relative_to: Optional[Path] = None,
        name_only: bool = False,
        add_bottom: bool = True,
        stack_level: int = 2,
    ):
        self.layout = layout
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
        return self.tracker.active

    def add(self, md_obj: MdObj) -> None:
        if self.add_bottom:
            self.obj_list.append(md_obj)
        else:
            self.obj_list.insert(0, md_obj)

    def md_obj(self, javascript_path: Path) -> MdObj:
        """
        Return the markdown object that represents output and code.
        """
        content = MdSeq(self.obj_list)
        if self.layout == "nocode":
            return content
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

            if self.layout == "top-c":
                return (
                    Admonition(
                        code_final,
                        javascript_path=javascript_path,
                        collapse=True,
                        title="Code",
                        kind="code",
                    )
                    + content
                    + HLine()
                )
            elif self.layout == "top-o":
                return code_final + content + HLine()
            elif self.layout == "bottom-c":
                return (
                    content
                    + Admonition(
                        code_final,
                        javascript_path=javascript_path,
                        collapse=True,
                        title="Code",
                        kind="code",
                    )
                    + HLine()
                )
            elif self.layout == "bottom-o":
                return content + code_final + HLine()
            elif self.layout == "tabbed":
                return (
                    Tab(content, title="Content")
                    + Tab(code_final, title="Code")
                    + HLine()
                )
            else:
                raise Exception("Unknown layout type.")
