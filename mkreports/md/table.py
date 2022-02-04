import copy
import inspect
import json
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

import pandas as pd
from mkreports.settings import Settings

from .base import MdObj
from .file import File, relpath_html, true_stem
from .text import SpacedText


class Table(MdObj):
    table: pd.DataFrame
    kwargs: Dict[str, Any]

    def __init__(self, table: pd.DataFrame, **kwargs):
        super().__init__()
        self.kwargs = kwargs
        # think about making this a static-frame
        self.table = deepcopy(table)

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        table_md = self.table.to_markdown(**self.kwargs)
        table_md = table_md if table_md is not None else ""
        return SpacedText(table_md, (2, 2))


class DataTable(File):
    def __init__(
        self,
        table: pd.DataFrame,
        store_path: Path,
        table_id: Union[str, Callable[[str], str]] = lambda hash: f"datatable-{hash}",
        column_settings: Optional[dict] = None,
        **kwargs,
    ):
        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("datatable.json")
            # here we use the split method; the index and columns
            # are not useful, but the rest gets set as 'data', which we need
            table.to_json(path, orient="split", **kwargs)

            # Make sure the file is moved to the right place
            super().__init__(
                path=path, store_path=store_path, allow_copy=True, use_hash=True
            )

        # use the hashed table name as the id if there is no other
        if isinstance(table_id, Callable):
            self.table_id = table_id(self.hash)
        else:
            self.table_id = table_id

        # prepare the table settings
        col_set = {col: {"title": col} for col in table.columns}
        if column_settings is not None:
            # only pick out settings for columns that occur in the table
            col_set.update({col: column_settings[col] for col in table.columns})

        # put together the settings for the table
        # there, the columns are a list in the correct order
        self.table_settings = {
            "scrollX": "true",
            "columns": [col_set[col] for col in table.columns],
        }

    def req_settings(self):
        settings = Settings(
            page=dict(
                # the following needs to be loaded in the header of the page, not the footer
                # this enables activating the tables in the body
                javascript=[
                    "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js",
                    "https://cdn.datatables.net/1.11.3/js/jquery.dataTables.min.js",
                ],
                css=["https://cdn.datatables.net/1.11.3/css/jquery.dataTables.min.css"],
            )
        )
        return settings

    def to_markdown(self, page_path: Path):
        if page_path is None:
            raise ValueError(
                "page_path must be set for relative referencing of json data file."
            )

        # now we insert the data table on the page
        # note: as we are inserting directly into html, we have to do one addition
        # level deeper for the relative path
        rel_table_path = relpath_html(self.path, page_path)
        table_settings = copy.deepcopy(self.table_settings)
        table_settings["ajax"] = str(rel_table_path)
        settings_str = json.dumps(table_settings)
        raw_html = inspect.cleandoc(
            f"""
            <table id='{self.table_id}' class='display' style='width:100%'> </table>
            <script>
            $(document).ready( function () {{
            $('#{self.table_id}').DataTable({settings_str});
            }} );
            </script>
            """
        )

        return SpacedText(raw_html, (2, 2))


class Tabulator(File):
    def __init__(
        self,
        table: pd.DataFrame,
        store_path: Path,
        table_id: Union[str, Callable[[str], str]] = lambda hash: f"tabulator-{hash}",
        column_settings: Optional[dict] = None,
        **kwargs,
    ):
        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("tabulator.json")
            # here we use the split method; the index and columns
            # are not useful, but the rest gets set as 'data', which we need
            table.to_json(path, orient="records", **kwargs)

            # Make sure the file is moved to the right place
            super().__init__(
                path=path, store_path=store_path, allow_copy=True, use_hash=True
            )

        # use the hashed table name as the id if there is no other
        if isinstance(table_id, Callable):
            self.table_id = table_id(self.hash)
        else:
            self.table_id = table_id

        # prepare the table settings
        col_set = {col: {"title": col} for col in table.columns}
        if column_settings is not None:
            # only pick out settings for columns that occur in the table
            col_set.update({col: column_settings[col] for col in table.columns})

        self.table_settings: Dict[str, Any] = dict(
            autoColumns=True,
            pagination=True,
            paginationSize=10,
            paginationSizeSelector=True,
        )

    def req_settings(self):
        settings = Settings(
            page=dict(
                # the following needs to be loaded in the header of the page, not the footer
                # this enables activating the tables in the body
                javascript=[
                    "https://unpkg.com/tabulator-tables@5.1.0/dist/js/tabulator.min.js",
                ],
                css=[
                    "https://unpkg.com/tabulator-tables@5.1.0/dist/css/tabulator.min.css"
                ],
            )
        )
        return settings

    def to_markdown(self, page_path: Path):
        if page_path is None:
            raise ValueError(
                "page_path must be set for relative referencing of json data file."
            )

        # now we insert the data table on the page
        # note: as we are inserting directly into html, we have to do one addition
        # level deeper for the relative path
        rel_table_path = relpath_html(self.path, page_path)
        table_settings = copy.deepcopy(self.table_settings)
        table_settings["ajaxURL"] = str(rel_table_path)
        settings_str = json.dumps(table_settings)
        raw_html = inspect.cleandoc(
            f"""
            <div id='{self.table_id}' class='display' style='width:100%'> </div>
            <script>
            var table = new Tabulator('#{self.table_id}', {settings_str});
            </script>
            """
        )

        return SpacedText(raw_html, (2, 2))
