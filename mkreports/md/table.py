import inspect
import tempfile
from pathlib import Path
from typing import Optional

import pandas as pd

from .base import MdObj
from .file import File, relpath, true_stem
from .text import SpacedText


class Table(MdObj):
    def __init__(self, table: pd.DataFrame, **kwargs):
        self.kwargs = kwargs
        self.table = table

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        table_md = self.table.to_markdown(**self.kwargs)
        table_md = table_md if table_md is not None else ""
        return SpacedText(table_md, (2, 2))


class DataTable(File):
    def __init__(
        self,
        table: pd.DataFrame,
        store_path: Path,
        table_id: Optional[str] = None,
        **kwargs,
    ):
        self.kwargs = kwargs

        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("table.json.gzip")
            table.to_json(path, **kwargs)

            # Make sure the file is moved to the rigth place
            super().__init__(
                path=path, store_path=store_path, allow_copy=True, hash=True
            )

        # use the hashed table name as the id if there is no other
        if table_id is None:
            table_id = true_stem(self.path)
        self.table_id = table_id

    def requirements(self):
        settings = dict(
            # the following needs to be loaded in the header of the page, not the footer
            # this enables activating the tables in the body
            extra_javascript=[
                "https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js",
                "https://cdn.datatables.net/1.11.3/js/jquery.dataTables.min.js",
            ],
            extra_css=[
                "https://cdn.datatables.net/1.11.3/css/jquery.dataTables.min.css"
            ],
        )
        return settings

    def to_markdown(self, page_path: Path):
        if page_path is None:
            raise ValueError(
                "page_path must be set for relative referencing of json data file."
            )

        # now we insert the data table on the page
        rel_table_path = str(relpath(self.path, page_path.parent))
        raw_html = inspect.cleandoc(
            f"""
            <table id='{self.table_id}' class='display' style='width:100%'> </table>
            <script>
            $(document).ready( function () {{
            $('#{self.table_id}').DataTable({{
                'ajax': '{rel_table_path}'
            }});
            }} );
            </script>
        """
        )

        return SpacedText(raw_html, (2, 2))
