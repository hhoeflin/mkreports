from pathlib import Path
from typing import Optional

from mkreports.md_proxy import register_md

from .base import MdObj, MdOut, Raw
from .containers import Admonition, CodeFile
from .text import SpacedText


@register_md("HLine")
class HLine(Raw):
    def __init__(self):
        super().__init__(SpacedText("---", (2, 2)))


@register_md("CollapsedCodeFile")
class CollapsedCodeFile(MdObj):
    def __init__(
        self,
        file: Path,
        store_path: Path,
        report_path: Path,
        javascript_path: Path,
        title: Optional[str] = None,
    ) -> None:
        self.obj = Admonition(
            CodeFile(file, title=title, store_path=store_path, report_path=report_path),
            collapse=True,
            title="Code",
            kind="code",
            javascript_path=javascript_path,
        )

    def to_markdown(self, **kwargs) -> MdOut:
        md_out = self.obj.to_markdown(**kwargs)
        return md_out
