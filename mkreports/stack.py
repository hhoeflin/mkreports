import inspect
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from .md.base import Code


@dataclass
class FrameInfo:
    filename: str
    code_range: Tuple[int, int]
    display_range: Tuple[int, int]
    currentline_idx: int
    code: List[str]

    def __str__(self):
        header = f"File: {self.filename}"
        position = f" {self.display_range} in {self.code_range}"
        return "\n".join([header, position, self.display_code])

    @property
    def display_code(self):
        display_code = "".join(
            self.code[
                (self.display_range[0] - self.code_range[0]) : (
                    self.display_range[1] - self.code_range[1]
                )
            ]
        )
        return display_code

    def md_code(self, code_range=True, highlight=True):
        if code_range:
            code = "".join(self.code)
            first_line = self.code_range[0] + 1
        else:
            code = self.display_code
            first_line = self.code_range[0] + 1

        if highlight and code_range:
            hi_lines = (self.display_range[0] + 1, self.display_range[1] + 1)
        else:
            hi_lines = None

        return Code(
            code=code,
            title=self.filename,
            first_line=first_line,
            hi_lines=hi_lines,
            language="python",
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


def get_stack() -> Stack:
    """
    Get a simplified version of the stack.
    """
    curframe = inspect.currentframe()
    if curframe is not None:
        frame = curframe.f_back
    else:
        raise Exception("Can't happen!")

    stack = []
    while frame is not None:
        code = frame.f_code
        higher_frame = frame.f_back

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
        stack.append(
            FrameInfo(
                filename=code.co_filename,
                code_range=(
                    code.co_firstlineno - 1,
                    code.co_firstlineno - 1 + len(code_lines),
                ),
                display_range=(code.co_firstlineno - 1, frame.f_lineno),
                currentline_idx=frame.f_lineno - 1,
                code=code_lines,
            )
        )
        frame = higher_frame
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
                if frame_old.display_range == frame_new.display_range:
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
                            display_range=(frame.currentline_idx, frame.code_range[1]),
                            currentline_idx=frame.code_range[1],
                            code=frame.code,
                        )
                        for frame in self.first[idx + 1 :]
                    ]
                    middle_frame = copy(self.first[idx])
                    middle_frame.display_range = (
                        self.first[idx].display_range[1] - 1,
                        self.second[idx].display_range[1],
                    )
                    self.middle = [middle_frame]
                    self.new_lower = [frame for frame in self.second[idx + 1 :]]
                    self.changed = self.old_lower + self.middle + self.new_lower
                    return
