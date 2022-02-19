from pathlib import Path
from typing import Optional

from .base import MdObj, Raw
from .containers import Admonition, CodeFile
from .md_proxy import register_md
from .settings import PageInfo
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
        page_info: PageInfo,
        title: Optional[str] = None,
    ) -> None:
        self.obj = Admonition(
            CodeFile(file, title=title, page_info=page_info),
            collapse=True,
            title="Code",
            kind="code",
            page_info=page_info,
        )

        self._body = self.obj.body
        self._back = self.obj.back
        self._settings = self.obj.settings
