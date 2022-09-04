import logging
from copy import deepcopy
from typing import Any, Dict, Optional, Set

import attrs
import pandas as pd

from mkreports.md.base import MdObj, RenderedMd
from mkreports.md.md_proxy import register_md
from mkreports.md.text import SpacedText

logger = logging.getLogger(__name__)


@register_md("Table")
@attrs.mutable(init=False)
class Table(MdObj):
    """
    Standard markdown table.

    Args:
        table (pd.DataFrame): The table to include in pandas format.
        max_rows (Optional[int]): Maximum number of rows. If None, all will
            be included. If longer, a warning will be logged and the first `max_rows`
            will be included.
    """

    table: pd.DataFrame
    kwargs: Dict[str, Any]

    def __init__(self, table: pd.DataFrame, max_rows: Optional[int] = 100, **kwargs):
        Table.__attrs_init__(self, table=table, kwargs=kwargs)  # type: ignore
        # think about making this a static-frame
        self.table = deepcopy(self.table)
        if max_rows is not None and table.shape[0] > max_rows:
            logger.warning(
                f"Table has {table.shape[0]} rows, but only {max_rows} allowed. Truncating."
            )
            self.table = self.table.iloc[0:max_rows]

    def _render(self) -> RenderedMd:  # type: ignore
        # check if the table has too many rows
        table_md = self.table.to_markdown(**self.kwargs)  # type: ignore
        table_md = table_md if table_md is not None else ""

        body = SpacedText(table_md, (2, 2))
        back = None
        settings = None
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return set()
