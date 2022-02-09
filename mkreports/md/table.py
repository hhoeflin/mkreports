import copy
import inspect
import json
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from mkreports.md_proxy import register_md
from mkreports.utils import snake_to_text
from pandas.api import types

from .base import MdObj, MdOut, comment_ids
from .file import File, relpath_html
from .idstore import IDStore
from .settings import Settings, merge_settings
from .text import SpacedText


@register_md("Table")
class Table(MdObj):
    table: pd.DataFrame
    kwargs: Dict[str, Any]

    def __init__(self, table: pd.DataFrame, **kwargs):
        super().__init__()
        self.kwargs = kwargs
        # think about making this a static-frame
        self.table = deepcopy(table)

    def to_markdown(self, **kwargs) -> MdOut:
        del kwargs
        table_md = self.table.to_markdown(**self.kwargs)
        table_md = table_md if table_md is not None else ""
        return MdOut(body=SpacedText(table_md, (2, 2)))


@register_md("DataTable")
class DataTable(File):
    def __init__(
        self,
        table: pd.DataFrame,
        store_path: Path,
        column_settings: Optional[dict] = None,
        **kwargs,
    ):
        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("datatable.json")
            # here we use the split method; the index and columns
            # are not useful, but the rest gets set as 'data', which we need
            table.to_json(path, orient="split", default_handler=str, **kwargs)

            # Make sure the file is moved to the right place
            super().__init__(
                path=path, store_path=store_path, allow_copy=True, use_hash=True
            )

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

    def to_markdown(self, page_path: Path, idstore: IDStore, **kwargs) -> MdOut:
        del kwargs
        datatable_id = idstore.next_id("datatable_id")
        body_html = inspect.cleandoc(
            f"""
            <table id='{datatable_id}' class='display' style='width:100%'> </table>
            """
        )

        rel_table_path = relpath_html(self.path, page_path)
        table_settings = copy.deepcopy(self.table_settings)
        table_settings["ajax"] = str(rel_table_path)
        settings_str = json.dumps(table_settings)
        back_html = inspect.cleandoc(
            f"""
            <script>
            $(document).ready( function () {{
            $('#{datatable_id}').DataTable({settings_str});
            }} );
            </script>
            """
        )
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

        return MdOut(
            body=SpacedText(body_html, (2, 2)),
            back=SpacedText(back_html, (2, 2)) + comment_ids(datatable_id),
            settings=settings,
        )


def series_to_filter(series: pd.Series) -> Dict[str, Any]:
    if types.is_bool_dtype(series.dtype):
        return dict(
            headerFilter="tickCross",
            formatter="tickCross",
            headerFilterParams=dict(tristate=True),
        )
    if types.is_categorical_dtype(series.dtype):
        return dict(
            headerFilter="select",
            headerFilterParams=dict(
                values=[""] + series.cat.categories.values.tolist(),
            ),
        )
    if types.is_numeric_dtype(series.dtype):
        return dict(
            width=80,
            headerFilter="minMaxFilterEditor",
            headerFilterFunc="minMaxFilterFunction",
            headerFilterLiveFilter=False,
        )
    return dict(headerFilter="input")


@register_md("Tabulator")
class Tabulator(File):
    def __init__(
        self,
        table: pd.DataFrame,
        store_path: Path,
        javascript_path: Path,
        table_settings: Optional[dict] = None,
        add_header_filters: bool = True,
        prettify_colnames: bool = True,
        column_settings: Optional[dict] = None,
        **kwargs,
    ):
        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("tabulator.json")
            # here we use the split method; the index and columns
            # are not useful, but the rest gets set as 'data', which we need
            table.to_json(path, orient="records", default_handler=str, **kwargs)

            # Make sure the file is moved to the right place
            super().__init__(
                path=path, store_path=store_path, allow_copy=True, use_hash=True
            )

        # create the javascript file
        self.min_max_filter_path = javascript_path / "min_max_filter.js"
        self.min_max_filter_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(
            Path(__file__).parent / "tabulator_js" / "min_max_filter.js",
            self.min_max_filter_path,
        )

        # produce the column settings
        col_set_dict = {}
        for colname in table.columns:
            assert isinstance(colname, str)
            inner_dict: Dict[str, Any] = {"field": colname}
            if add_header_filters:
                # depending on the type of the column, choose a different filter
                filter_dict = series_to_filter(table[colname])
                inner_dict.update(filter_dict)
            if prettify_colnames:
                inner_dict["title"] = snake_to_text(colname)
            else:
                inner_dict["title"] = colname
            col_set_dict[colname] = inner_dict
        col_set_dict = merge_settings(
            col_set_dict, column_settings if column_settings is not None else {}
        )

        col_list = list(col_set_dict.values())

        # put the other settings together
        self.table_settings: Dict[str, Any] = merge_settings(
            dict(
                layout="fitDataTable",
                pagination=True,
                paginationSize=10,
                paginationSizeSelector=True,
            ),
            table_settings if table_settings is not None else {},
        )
        self.table_settings["columns"] = col_list

    def to_markdown(self, page_path: Path, idstore: IDStore, **kwargs) -> MdOut:
        del kwargs

        tabulator_id = idstore.next_id("tabulator_id")
        body_html = inspect.cleandoc(
            f"""
            <div id='{tabulator_id}' class='display'> </div>
            """
        )

        rel_filter_path = relpath_html(self.min_max_filter_path, page_path)
        rel_table_path = relpath_html(self.path, page_path)
        table_settings = copy.deepcopy(self.table_settings)
        table_settings["ajaxURL"] = str(rel_table_path)

        # here we have to be careful to remove the '' around
        # the minMaxFilter function reference
        settings_str = json.dumps(table_settings)
        settings_str = settings_str.replace(
            '"minMaxFilterFunction"', "minMaxFilterFunction"
        )
        settings_str = settings_str.replace(
            '"minMaxFilterEditor"', "minMaxFilterEditor"
        )

        back_html = inspect.cleandoc(
            f"""
            <script>
            var table = new Tabulator('#{tabulator_id}', {settings_str});
            </script>
            """
        )
        settings = Settings(
            page=dict(
                # the following needs to be loaded in the header of the page, not the footer
                # this enables activating the tables in the body
                javascript=[
                    "https://unpkg.com/tabulator-tables@5.1.0/dist/js/tabulator.min.js",
                    rel_filter_path,
                ],
                css=[
                    "https://unpkg.com/tabulator-tables@5.1.0/dist/css/tabulator.min.css"
                ],
            )
        )

        return MdOut(
            body=SpacedText(body_html, (2, 2)),
            back=SpacedText(back_html, (2, 2)) + comment_ids(tabulator_id),
            settings=settings,
        )
