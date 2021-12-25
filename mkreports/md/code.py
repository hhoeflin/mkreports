import html
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from mdutils.tools.TextUtils import TextUtils

from .base import MdObj
from .text import SpacedText


@dataclass(frozen=True)
class Code(MdObj):
    """Wrapper class for code."""

    code: str
    title: Optional[str] = None
    first_line: Optional[int] = None
    hl_lines: Optional[Tuple[int, int]] = None
    language: Optional[str] = "python"

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        annots = ""
        if self.language is not None:
            annots = annots + self.language
        if self.title is not None:
            annots = annots + f' title="{html.escape(self.title)}"'
        if self.first_line is not None:
            # hi_lines get intrepreted relative to first_line
            if self.hl_lines is not None:
                hl_lines = (
                    self.hl_lines[0] - self.first_line + 1,
                    self.hl_lines[1] - self.first_line + 1,
                )
            else:
                hl_lines = self.hl_lines
            annots = annots + f' linenums="{self.first_line}"'
        else:
            hl_lines = self.hl_lines

        if hl_lines is not None:
            annots = annots + f' hl_lines="{hl_lines[0]}-{hl_lines[1]}"'

        return SpacedText(TextUtils.insert_code(self.code, annots), (2, 2))


def get_code_context(enclose: int = 0, omit_frames: int = 0) -> Code:
    """
    Get a code object that represents a context around the area where the
    function is being called.

    The `omit_frames` argument specifies how many frames to go up to find
    the place relative to which code should be extracted. `enclose` gives the
    number of code levels to go up, referring to statements that enclose the
    current statements. `stmts` then gives the number of statements before and after
    to include (after going up according to `enclose`.
    """
    pass
