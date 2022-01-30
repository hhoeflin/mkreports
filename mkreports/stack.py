from __future__ import annotations

import inspect
import logging
import sys
from copy import copy
from pathlib import Path
from textwrap import dedent
from types import FrameType, ModuleType
from typing import List, Optional, Sequence, Tuple, Union

from anytree import NodeMixin
from intervaltree import Interval

from . import parser
from .exceptions import TrackerActiveError, TrackerNotActiveError
from .md import Code, MdObj, Raw, Tab

logger = logging.getLogger(__name__)

AnyPath = Union[str, Path]


class Tracker:
    """
    Used to profile the code in order to detect executed functions.

    It is intended to be used as a context manager. When entering
    the context, the profiler will be set and all subsequent
    function calls will be recorded. Afterwards the profiling
    is stopped.
    """

    def __init__(
        self,
        dirs: Optional[Union[AnyPath, Sequence[AnyPath]]] = None,
        packages: Optional[Union[ModuleType, Sequence[ModuleType]]] = None,
        omit_levels: int = 0,
    ):
        if isinstance(dirs, Sequence) and not isinstance(dirs, str):
            my_dirs = list(dirs)  # don't need to do anything
        elif isinstance(dirs, (str, Path)):
            my_dirs = [dirs]
        else:
            my_dirs = []

        if isinstance(packages, Sequence):
            packages = list(packages)
        elif isinstance(packages, ModuleType):
            packages = [packages]
        else:
            packages = []

        # for the packages, we also convert them to directories
        for package in packages:
            # always use the first element of the list
            my_dirs.append(Path(package.__path__[0]))

        # make the directories strings with a slash at the end
        self.dirs = [str(x) + "/" for x in my_dirs]

        self.omit_levels = omit_levels
        self.ctx_active = False
        self.tree = None
        self.cur_node = None

    def start(self, omit_levels=0):
        """Activate the tracking."""
        if self.ctx_active:
            raise TrackerActiveError("Context manager is already active")

        frame = self._get_callee_frame(omit_levels=omit_levels + 1)
        # save the tree for storing the information
        self.tree = FrameInfo.from_frame(frame)

        # include the current file in the directories to accept
        self.active_dirs = copy(self.dirs)
        self.active_dirs.append(str(Path(self.tree.filename).parent) + "/")
        self.active_dirs = list(set(self.active_dirs))

        # here we actually want the next command
        self.cur_node = self.tree
        stmt_tree = parser.get_stmt_ranges(Path(frame.f_code.co_filename))
        stmt_after = parser.closest_after(stmt_tree, frame.f_lineno)
        if stmt_after is None:
            self.entry_lineno = frame.f_lineno
        else:
            self.entry_lineno = stmt_after.begin
        self.ctx_active = True

        # we get the directory of the callee
        if sys.gettrace() is None:
            sys.settrace(self.trace)
            # sys.settrace(None)
        else:
            logger.warning(f"Logger already set to {sys.gettrace()}")

        return self

    def stop(self, omit_levels=0):
        if not self.ctx_active:
            raise TrackerNotActiveError("Context manager is not active")

        sys.settrace(None)
        frame = self._get_callee_frame(omit_levels=omit_levels + 1)
        # we set the display range
        # the display_range should go to the end of the current statement
        if self.tree is not None:
            # here we want to have the true ending line number
            stmt_tree = parser.get_stmt_ranges(Path(frame.f_code.co_filename))
            cur_stmt_lines = parser.smallest_overlap(stmt_tree, frame.f_lineno)
            if cur_stmt_lines is not None:
                self.tree.hilite_interval = Interval(
                    self.entry_lineno, cur_stmt_lines.end
                )
            else:
                raise Exception("Could not find current statement")
        else:
            raise Exception("__enter__ has not been called.")
        self.ctx_active = False

    def __enter__(self) -> "Tracker":
        """Enter context manager and set the profiler."""
        return self.start(omit_levels=1)

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        """Remove the profiler when exiting the context manager."""
        self.stop(omit_levels=1)

    @property
    def finished(self) -> bool:
        """Tracker ctx manager has been finished."""
        # The tracker context manager has been finished if
        # the node is not None, but also the ctx-manager is not active.
        return self.tree is not None and not self.ctx_active

    def _get_callee_frame(self, omit_levels: int) -> FrameType:
        frame = inspect.currentframe()
        # need to jump over the specified number of levels
        for _ in range(omit_levels + 1):
            if frame is None:
                raise Exception("frame is None")
            frame = frame.f_back
        if frame is None:
            raise Exception("frame is None")
        return frame

    def frame_traceable(self, frame: FrameType) -> bool:
        frame_path = frame.f_code.co_filename
        for dir in self.active_dirs:
            if frame_path.startswith(dir):
                return True
        return False

    def notrace(self, frame, event, arg):
        return None

    def trace_reset_on_return(self, frame, event, arg):
        if event == "return":
            sys.settrace(self.trace)
            return self.trace

    def trace(self, frame, event, arg):
        # when tracing, only care if it is a 'call' event
        if event == "call":
            # if it is inside the approved dirs, keep tracing;
            # otherwise we turn it off
            if self.frame_traceable(frame):
                # add the code object to the things that are traced
                # we put this as part of the tree
                self.cur_node = FrameInfo.from_frame(frame, parent=self.cur_node)
                return self.trace
            else:
                # we stop tracing
                sys.settrace(self.notrace)
                return self.trace_reset_on_return
        elif event == "return":
            # set the current node to the parent in the tree
            if self.cur_node is not None:
                self.cur_node = self.cur_node.parent
                sys.settrace(self.trace)
            else:
                raise Exception("cur_node should not be None")
            pass
        else:
            return self.trace


class FrameInfo(NodeMixin):
    filename: str
    code_interval: Interval
    hilite_interval: Optional[Interval]
    curlineno: int
    code: List[str]
    co_name: str

    def __init__(
        self,
        filename: str,
        code_interval: Interval,
        hilite_interval: Optional[Interval],
        curlineno: int,
        code: List[str],
        co_name: str,
        parent: Optional[FrameInfo],
        children: Optional[List[FrameInfo]],
    ):
        self.filename = filename
        self.code_interval = code_interval
        self.hilite_interval = hilite_interval
        self.curlineno = curlineno
        self.code = code
        self.co_name = co_name
        self.parent = parent
        if children:
            self.children = children

    def __str__(self):
        header = f"File: {self.filename}"
        position = f" {self.hilite_interval} in {self.code_interval}"
        return "\n".join([header, position, self.focus_code])

    @property
    def name(self):
        return f"{self.filename}:{self.code_interval.begin}-{self.code_interval.end}"

    @property
    def focus_interval(self):
        if self.hilite_interval is None:
            return self.code_interval
        else:
            return self.hilite_interval

    @property
    def focus_code(self):
        display_code = "".join(
            self.code[
                (self.focus_interval.begin - self.code_interval.begin) : (
                    self.focus_interval.end - self.code_interval.begin
                )
            ]
        )
        return display_code

    def md_code(self, highlight: bool = True, full_filename: bool = False) -> Code:
        if highlight:
            code = "".join(self.code)
            first_line = self.code_interval.begin
            if self.code_interval == self.focus_interval:
                hl_lines = None
            else:
                hl_lines = (self.focus_interval.begin, self.focus_interval.end - 1)
        else:
            # no highlight, so we take the focused range
            code = self.focus_code
            first_line = self.focus_interval.begin
            hl_lines = None

        return Code(
            code=dedent(code),
            title=self.filename if full_filename else Path(self.filename).name,
            first_line=first_line,
            hl_lines=hl_lines,
            language="python",
        )

    def _md_collect(self, highlight) -> List[Tuple[str, Code]]:
        res = [(self.co_name, self.md_code(highlight=highlight))]
        for child in self.children:
            res.extend(child._md_collect(highlight))
        return res

    def md_tree(self, highlight: bool = True, full_filename: bool = False) -> MdObj:
        """
        Return the code in a tree.

        If there is only a single node, a simple Code object is returned,
        otherwise Tabs are produced for the code. In the tabs,
        functions that occur earlier in the code are listed first.
        Also, functions are only listed once even if they occur deeper in the
        tree.
        """
        code_list = self._md_collect(highlight)

        # now only take the unique ones
        code_list = list({key: None for key in code_list}.keys())
        # now we want to de-duplicate the list

        if len(code_list) > 0:
            if len(code_list) == 1:
                return code_list[0][1]
            else:
                res = Tab(code_list[0][1], title="<main>")
                for i in range(1, len(code_list)):
                    res = res + Tab(
                        code_list[i][1],
                        title=code_list[i][0]
                        if full_filename
                        else Path(code_list[i][0]).name,
                    )
                return res
        else:
            return Raw("")

    @classmethod
    def from_frame(cls, frame, parent=None, children=None) -> "FrameInfo":
        code = frame.f_code

        # if higher_frame is None and code.co_firstlineno != 1:
        #    raise Exception(
        #        f"Did not expect first line {code.co_firstlineno} when upper frame is None."
        #    )
        # if higher_frame is None:
        #    code_lines = read_file(Path(code.co_filename))
        # else:
        try:
            if code.co_name == "<module>":
                code_lines = read_file(Path(code.co_filename))
            else:
                code_lines = inspect.getsourcelines(code)[0]
        except Exception:
            code_lines = ["Count not get source\n"]
        return FrameInfo(
            filename=code.co_filename,
            co_name=code.co_name,
            code_interval=Interval(
                code.co_firstlineno,
                code.co_firstlineno + len(code_lines),
            ),
            hilite_interval=None,
            curlineno=frame.f_lineno,
            code=code_lines,
            parent=parent,
            children=children,
        )


Stack = List[FrameInfo]


def read_file(
    path: Path, from_line: Optional[int] = None, to_line: Optional[int] = None
) -> List[str]:

    """
    Read a part of a file.

    Reads a file from a line to a certain line. All line numbers are assumed to
    start with 0.
    """
    with path.open("r") as f:
        lines = f.readlines()

    return lines[slice(from_line, to_line, 1)]


def get_stack(omit_levels: int = 0) -> Stack:
    """
    Get a simplified version of the stack.
    """
    frame = inspect.currentframe()
    # need to jump over the specified number of levels
    for _ in range(omit_levels + 1):
        if frame is None:
            raise Exception("frame is None")
        frame = frame.f_back

    stack = []
    while frame is not None:
        stack.append(FrameInfo.from_frame(frame))
        frame = frame.f_back
    return list(reversed(stack))


class StackDiff:
    def __init__(self, first_stack: Stack, second_stack: Stack):
        """
        Calculate the difference of two stacks.

        Shows the code executed between the old stack and the new.
        """
        self.first = first_stack
        self.second = second_stack

        self.equal = []
        for idx in range(min(len(self.first), len(self.second))):
            frame_old = self.first[idx]
            frame_new = self.second[idx]
            if (
                frame_old.filename == frame_new.filename
                and frame_old.code_interval == frame_new.code_interval
            ):
                # this is within the same function
                if frame_old.hilite_interval == frame_new.hilite_interval:
                    # this is the same, no change
                    self.equal.append(frame_old)
                else:
                    # execution has at least moved by one code line
                    # store the lower levels of the old frame
                    # then the difference in the current frame to the new
                    # then the lower levels of the new frame
                    self.old_lower = [
                        FrameInfo(
                            filename=frame.filename,
                            code_interval=frame.code_interval,
                            hilite_interval=Interval(
                                frame.curlineno, frame.code_interval.end
                            ),
                            curlineno=frame.code_interval.end,
                            code=frame.code,
                            co_name=frame.co_name,
                            parent=None,
                            children=None,
                        )
                        for frame in self.first[idx + 1 :]
                    ]
                    middle_frame = copy(self.first[idx])
                    middle_frame.hilite_interval = Interval(
                        self.first[idx].focus_interval.end - 1,
                        self.second[idx].focus_interval.end,
                    )
                    self.middle = [middle_frame]
                    self.new_lower = [frame for frame in self.second[idx + 1 :]]
                    self.changed = self.old_lower + self.middle + self.new_lower
                    return
