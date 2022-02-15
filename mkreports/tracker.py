import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import List, Optional

from . import parser
from .exceptions import (CannotTrackError, TrackerEmptyError,
                         TrackerNotActiveError)
from .md import Code


@dataclass
class CodeBlock:
    filename: str
    co_name: str
    line_start: int
    line_end: int

    def md_code(
        self, relative_to: Optional[Path] = None, name_only: bool = False
    ) -> Code:
        code = dedent(
            read_file(
                Path(self.filename),
                from_line=self.line_start,
                to_line=self.line_end,
            )
        )

        try:
            assert relative_to is not None
            filename_to_use = str(Path(self.filename).relative_to(relative_to))
        except Exception:
            if name_only:
                filename_to_use = Path(self.filename).name
            else:
                filename_to_use = self.filename

        return Code(
            code=code,
            title=filename_to_use,
            first_line=self.line_start,
            language="python",
        )


def read_file(
    path: Path, from_line: Optional[int] = None, to_line: Optional[int] = None
) -> str:

    """
    Read a part of a file.

    Reads a file from a line to a certain line. All line numbers are assumed to
    start with 0.
    """
    with path.open("r") as f:
        lines = f.readlines()

    # the from_line to_line are line-numbers, not indices. to_line is included
    return "".join(
        lines[slice(from_line - 1 if from_line is not None else None, to_line, 1)]
    )


class BaseTracker(ABC):
    @abstractmethod
    def start(self, frame_info: inspect.FrameInfo) -> None:
        pass

    @abstractmethod
    def stop(self, frame_info: inspect.FrameInfo) -> None:
        pass

    @abstractmethod
    def code(self) -> List[CodeBlock]:
        pass

    @property
    @abstractmethod
    def active(self) -> bool:
        pass


class SimpleTracker(BaseTracker):
    """
    Track first and last line of a code context.

    When starting it records the line after the current
    statement, and stopping the line where the current statement ends.

    The first and last line are required to be in the same file.
    """

    def __init__(self):
        self._active = False
        self.line_start = None
        self.line_end = None
        self.co_name = None

    def start(self, frame_info: inspect.FrameInfo) -> None:

        if frame_info.filename == "<stdin>":
            raise CannotTrackError(f"Cannot track {frame_info.filename}")

        self.stmt_tree = parser.get_stmt_ranges(Path(frame_info.filename))
        stmt_after = parser.closest_after(self.stmt_tree, frame_info.lineno)
        self.filename = frame_info.filename
        if stmt_after is None:
            self.line_start = frame_info.lineno
        else:
            self.line_start = stmt_after.begin
        self.co_name = frame_info.frame.f_code.co_name
        self._active = True

    def stop(self, frame_info: inspect.FrameInfo) -> None:
        if not self.active:
            raise TrackerNotActiveError("SimpleTracker not active")
        else:
            cur_stmt_lines = parser.smallest_overlap(self.stmt_tree, frame_info.lineno)
            if cur_stmt_lines is not None:
                self.line_end = cur_stmt_lines.end
            else:
                raise Exception("Could not find current statement")
        self._active = False

    def code(self) -> List[CodeBlock]:
        if (
            self.active
            or self.line_start is None
            or self.line_end is None
            or self.co_name is None
        ):
            raise TrackerEmptyError()
        else:
            return [
                CodeBlock(self.filename, self.co_name, self.line_start, self.line_end)
            ]

    @property
    def active(self) -> bool:
        return self._active
