import inspect
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


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
        display_code = "".join(
            self.code[
                (self.display_range[0] - self.code_range[0]) : (
                    self.display_range[1] - self.code_range[1]
                )
            ]
        )
        return "\n".join([header, position, display_code])


Stack = List[FrameInfo]

StackDiff = List["Stack"]


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

        if higher_frame is None and code.co_firstlineno != 1:
            raise Exception(
                f"Did not expect first line {code.co_firstlineno} when upper frame is None."
            )
        code_lines = (
            read_file(Path(code.co_filename))
            if higher_frame is None
            else inspect.getsourcelines(code)[0]
        )
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


def stack_diff(stack_old, stack_new) -> Tuple[Stack, StackDiff]:
    """
    Calculate the difference of two stacks.

    Shows the code executed between the old stack and the new.
    """
    equal_stack = []
    for idx_old, idx_new in zip(range(len(stack_old)), range(len(stack_new))):
        frame_old = stack_old[idx_old]
        frame_new = stack_new[idx_new]
        if (
            frame_old.filename == frame_new.filename
            and frame_old.code_range == frame_new.code_range
        ):
            # this is within the same function
            if frame_old.display_range == frame_new.display_range:
                # this is the same, no change
                equal_stack.append(frame_old)
            else:
                # execution has at least moved by one code line
                # store the lower levels of the old frame
                # then the difference in the current frame to the new
                # then the lower levels of the new frame
                old_stack_lower = [
                    FrameInfo(
                        filename=frame.filename,
                        code_range=frame.code_range,
                        display_range=(frame.currentline_idx, frame.code_range[1]),
                        currentline_idx=frame.code_range[1],
                        code=frame.code,
                    )
                    for frame in stack_old[idx_old + 1 :]
                ]
                middle_frame = copy(stack_old[idx_old])
                middle_frame.display_range = (
                    stack_old[idx_old].display_range[1],
                    stack_new[idx_new].display_range[1],
                )
                middle_stack = [middle_frame]
                new_stack_lower = [frame for frame in stack_new[idx_new + 1 :]]

    return (equal_stack, [old_stack_lower, middle_stack, new_stack_lower])
