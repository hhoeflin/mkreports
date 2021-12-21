from __future__ import annotations

import inspect
import logging
import sys
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from types import FrameType, ModuleType
from typing import List, Optional, Sequence, Tuple, Union

from anytree import NodeMixin

from .md import Code, MdObj, MdSeq, Tab

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
            self.dirs = set(dirs)  # don't need to do anything
        elif isinstance(dirs, (str, Path)):
            self.dirs = set([dirs])
        else:
            self.dirs = set()

        if isinstance(packages, Sequence):
            packages = list(packages)
        elif isinstance(packages, ModuleType):
            packages = [packages]
        else:
            packages = []

        # for the packages, we also convert them to directories
        for package in packages:
            # always use the first element of the list
            self.dirs.add(Path(package.__path__[0]))

        self.omit_levels = omit_levels

    def __enter__(self) -> "Tracker":
        """Enter context manager and set the profiler."""

        frame = self._get_callee_frame()
        # save the tree for storing the information
        self.tree = FrameInfo.from_frame(frame)
        self.dirs.add(Path(self.tree.filename).parent)

        self.cur_node = self.tree
        self.entry_lineno = frame.f_lineno

        # we get the directory of the callee
        if sys.gettrace() is None:
            sys.settrace(self.trace)
        else:
            logger.warning(f"Logger already set to {sys.gettrace()}")

        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        """Remove the profiler when exiting the context manager."""
        sys.settrace(None)
        frame = self._get_callee_frame()
        # we set the display range
        self.tree.hilite_range = slice(self.entry_lineno - 1, frame.f_lineno)

    def _get_callee_frame(self) -> FrameType:
        frame = inspect.currentframe()
        # need to jump over the specified number of levels
        for _ in range(self.omit_levels + 2):
            if frame is None:
                raise Exception("frame is None")
            frame = frame.f_back
        if frame is None:
            raise Exception("frame is None")
        return frame

    def frame_traceable(self, frame: FrameType) -> bool:
        frame_path = Path(frame.f_code.co_filename)
        for dir in self.dirs:
            if dir in frame_path.parents:
                return True
        return False

    def trace(self, frame, event, arg):
        # when tracing, only care if it is a 'call' event
        if event == "call":
            # if it is inside the approved dirs, keep tracing;
            # otherwise we turn it off
            if self.frame_traceable(frame):
                # add the code object to the things that are traced
                # we put this as part of the tree
                self.cur_node = FrameInfo.from_frame(frame, parent=self.cur_node)
                print(self.tree.children)
                return self.trace
            else:
                # we stop tracing
                return None
        elif event == "return":
            # set the current node to the parent in the tree
            if self.cur_node is not None:
                self.cur_node = self.cur_node.parent
            else:
                raise Exception("cur_node should not be None")
            pass
        else:
            return self.trace


class FrameInfo(NodeMixin):
    filename: str
    code_range: slice
    hilite_range: Optional[slice]
    currentline_idx: int
    code: List[str]
    co_name: str

    def __init__(
        self,
        filename: str,
        code_range: slice,
        hilite_range: Optional[slice],
        currentline_idx: int,
        code: List[str],
        co_name: str,
        parent: Optional[FrameInfo],
        children: Optional[List[FrameInfo]],
    ):
        self.filename = filename
        self.code_range = code_range
        self.hilite_range = hilite_range
        self.currentline_idx = currentline_idx
        self.code = code
        self.co_name = co_name
        self.parent = parent
        if children:
            self.children = children

    def __str__(self):
        header = f"File: {self.filename}"
        position = f" {self.hilite_range} in {self.code_range}"
        return "\n".join([header, position, self.focus_code])

    @property
    def name(self):
        return f"{self.filename}:{self.code_range.start}-{self.code_range.stop}"

    @property
    def focus_range(self):
        if self.hilite_range is None:
            return self.code_range
        else:
            return self.hilite_range

    @property
    def focus_code(self):
        display_code = "".join(
            self.code[
                (self.focus_range.start - self.code_range.start) : (
                    self.focus_range.stop - self.code_range.stop
                )
            ]
        )
        return display_code

    def md_code(self, highlight: bool = True) -> MdObj:
        if highlight:
            code = "".join(self.code)
            first_line = self.code_range.start + 1
            if self.code_range == self.focus_range:
                hi_lines = None
            else:
                hi_lines = (self.focus_range.start + 1, self.focus_range.stop + 1)
        else:
            # no highlight, so we take the focused range
            code = self.focus_code
            first_line = self.focus_range.start + 1
            hi_lines = None

        return Code(
            code=code,
            title=self.filename,
            first_line=first_line,
            hi_lines=hi_lines,
            language="python",
        )

    def md_tree(self, highlight: bool = True) -> MdObj:
        if self.children:
            res = Tab(self.md_code(highlight=highlight), title="...main...")
            for child in self.children:
                res += Tab(child.md_tree(highlight=highlight), title=child.co_name)
            return res
        else:
            return self.md_code(highlight=highlight)

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
            code_range=slice(
                code.co_firstlineno - 1,
                code.co_firstlineno - 1 + len(code_lines),
            ),
            hilite_range=None,
            currentline_idx=frame.f_lineno - 1,
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
                and frame_old.code_range == frame_new.code_range
            ):
                # this is within the same function
                if frame_old.hilite_range == frame_new.hilite_range:
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
                            code_range=frame.code_range,
                            hilite_range=slice(
                                frame.currentline_idx, frame.code_range.stop
                            ),
                            currentline_idx=frame.code_range.stop,
                            code=frame.code,
                            co_name=frame.co_name,
                            parent=None,
                            children=None,
                        )
                        for frame in self.first[idx + 1 :]
                    ]
                    middle_frame = copy(self.first[idx])
                    middle_frame.hilite_range = slice(
                        self.first[idx].focus_range.stop - 1,
                        self.second[idx].focus_range.stop,
                    )
                    self.middle = [middle_frame]
                    self.new_lower = [frame for frame in self.second[idx + 1 :]]
                    self.changed = self.old_lower + self.middle + self.new_lower
                    return
