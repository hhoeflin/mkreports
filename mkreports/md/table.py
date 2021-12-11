from pathlib import Path
from typing import Literal, Optional

import pandas as pd

from .base import MdObj
from .text import SpacedText


class Table(MdObj):
    def __init__(self, table: pd.DataFrame, **kwargs):
        self.kwargs = kwargs
        self.table = table

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        return SpacedText(self.table.to_markdown(**self.kwargs), (2, 2))
