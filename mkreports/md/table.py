import copy
import inspect
import logging
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from mkreports.utils import func_ref, serialize_json, snake_to_text
from pandas.api import types

from .base import MdObj, comment_ids
from .file import File, relpath_html, store_asset_relpath
from .md_proxy import register_md
from .settings import PageInfo, Settings, merge_settings
from .text import SpacedText

logger = logging.getLogger(__name__)


@register_md("Table")
class Table(MdObj):
    """Standard markdown table."""

    table: pd.DataFrame
    kwargs: Dict[str, Any]

    def __init__(self, table: pd.DataFrame, max_rows: Optional[int] = 100, **kwargs):
        """
        Initialize the table object.

        Args:
            table (pd.DataFrame): The table to include in pandas format.
            max_rows (Optional[int]): Maximum number of rows. If None, all will
                be included. If longer, a warning will be logged and the first `max_rows`
                will be included.
        """
        super().__init__()
        self.kwargs = kwargs
        # think about making this a static-frame
        self.table = deepcopy(table)

        # check if the table has too many rows
        if max_rows is not None and table.shape[0] > max_rows:
            logger.warning(
                f"Table has {table.shape[0]} rows, but only {max_rows} allowed. Truncating."
            )
            self.table = self.table.iloc[0:max_rows]

        table_md = self.table.to_markdown(**self.kwargs)
        table_md = table_md if table_md is not None else ""

        self._body = SpacedText(table_md, (2, 2))
        self._back = None
        self._settings = None


def _create_yadcf_settings_datatable(
    df: pd.DataFrame,
    yadcf_settings: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    # produce the column settings
    col_set_dict = {}
    for index, colname in enumerate(df.columns):
        assert isinstance(colname, str)
        # set the name of the column
        inner_dict: Dict[str, Any] = {"column_number": index}
        # only add header filters if requested
        filter_dict = _series_to_filter_yadcf(df[colname])
        inner_dict.update(filter_dict)
        col_set_dict[colname] = inner_dict
    col_set_dict = merge_settings(
        col_set_dict, yadcf_settings if yadcf_settings is not None else {}
    )

    col_list = list(col_set_dict.values())
    return col_list


def _series_to_filter_yadcf(series: pd.Series) -> Dict[str, Any]:
    if types.is_bool_dtype(series.dtype):
        return dict(
            filter_type="select",
        )
    if types.is_categorical_dtype(series.dtype):
        return dict(
            filter_type="select",
        )
    if types.is_numeric_dtype(series.dtype):
        return dict(
            filter_type="range_number",
        )
    return dict(filter_type="text")


@register_md("DataTable")
class DataTable(File):
    """Table using DataTable javascript library."""

    def __init__(
        self,
        table: pd.DataFrame,
        page_info: PageInfo,
        max_rows: Optional[int] = 1000,
        column_settings: Optional[dict] = None,
        prettify_colnames: bool = True,
        add_header_filters: bool = False,
        yadcf_settings: Optional[dict] = None,
        table_kwargs: Optional[dict] = None,
        downloads: bool = False,
        table_settings: Optional[dict] = None,
    ):
        """
        Initialize the table using the DataTable javascript library.

        Args:
            table (pd.DataFrame): The table in pandas.DataFrame format.
            page_info (PageInfo): PageInfo object for the page where the
                table should be located.
            max_rows (Optional[int]): Maximum number of rows. If None, all will
                be included. If longer, a warning will be logged and the first `max_rows`
                will be included.
            column_settings (Optional[dict]): Dict of settings for the columns. Will be
                passed as json to the DataTable library. Overrides any automatic settings.
            prettify_colnames (bool): Run colnames through 'snake_to_text' function.
            add_header_filters (bool): Should header filters be added.
            yadcf_settings (Optional[dict]): Settings for the *yadcf* header filter plugin.
                Overrides any automatic settings.
            table_kwargs (Optional[dict]): Keyword args for the table
                when serializing to json.
            downloads (bool): Should download buttons be shown?
            table_settings (Optional[dict]): Dictionary with the DataTable settings.
                Anything set here will overwrite existing ones.
        """
        assert page_info.idstore is not None
        assert page_info.page_path is not None

        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("datatable.json")
            # here we use the split method; the index and columns
            if max_rows is not None and table.shape[0] > max_rows:
                logger.warning(
                    f"Table has {table.shape[0]} rows, but only {max_rows} allowed. Truncating."
                )
                table = table.iloc[0:max_rows]
            # are not useful, but the rest gets set as 'data', which we need
            table.to_json(
                path,
                orient="split",
                default_handler=str,
                **(table_kwargs if table_kwargs is not None else {}),
            )

            # Make sure the file is moved to the right place
            super().__init__(
                path=path, page_info=page_info, allow_copy=True, use_hash=True
            )

        javascript_settings = [
            "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js",
            "https://cdn.datatables.net/1.11.3/js/jquery.dataTables.min.js",
            "https://cdn.jsdelivr.net/gh/vedmack/yadcf@332407eeacbda299e6253530e24c15041b270227/dist/jquery.dataTables.yadcf.js",
        ]
        css_settings = [
            "https://cdn.datatables.net/1.11.3/css/jquery.dataTables.min.css",
            "https://cdn.jsdelivr.net/gh/vedmack/yadcf@332407eeacbda299e6253530e24c15041b270227/dist/jquery.dataTables.yadcf.css",
        ]

        # prepare the table settings
        if prettify_colnames:
            col_set = {
                col: {"title": snake_to_text(col) if isinstance(col, str) else col}
                for col in table.columns
            }
        else:
            col_set = {col: {"title": col} for col in table.columns}
        if column_settings is not None:
            # only pick out settings for columns that occur in the table
            col_set.update({col: column_settings[col] for col in table.columns})

        self.add_header_filters = add_header_filters
        if add_header_filters:
            self.yadcf_settings = _create_yadcf_settings_datatable(
                table, yadcf_settings if yadcf_settings is not None else {}
            )

        # put together the settings for the table
        # there, the columns are a list in the correct order
        self.table_settings = {
            "scrollX": "true",
            "columns": [col_set[col] for col in table.columns],
        }

        if downloads:
            self.table_settings["buttons"] = ["copy", "csv", "excel", "pdf", "print"]
            # self.table_settings["dom"] = "Bfrtlp"
            self.table_settings["dom"] = "<lfr>t<Bp>"
            css_settings.append(
                "https://cdn.datatables.net/buttons/2.2.2/css/buttons.dataTables.min.css"
            )
            javascript_settings.extend(
                [
                    "https://cdn.datatables.net/buttons/2.2.2/js/dataTables.buttons.min.js",
                    "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js",
                    "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/pdfmake.min.js",
                    "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/vfs_fonts.js",
                    "https://cdn.datatables.net/buttons/2.2.2/js/buttons.html5.min.js",
                    "https://cdn.datatables.net/buttons/2.2.2/js/buttons.print.min.js",
                ]
            )

        datatable_id = page_info.idstore.next_id("datatable_id")
        body_html = inspect.cleandoc(
            f"""
            <table id='{datatable_id}' class='display' style='width:100%'> </table>
            """
        )

        rel_table_path = relpath_html(self.path, page_info.page_path)
        self.table_settings["ajax"] = str(rel_table_path)
        # overwrite with given settigns if necessary
        self.table_settings.update(table_settings if table_settings is not None else {})
        settings_str = serialize_json(self.table_settings)

        # prepare the header script if necessary
        if self.add_header_filters:
            yadcf_settings_str = serialize_json(self.yadcf_settings)
            yadcf_script = inspect.cleandoc(
                f"""
                yadcf.init(myTable, {yadcf_settings_str});
                """
            )
        else:
            yadcf_script = ""

        back_html = inspect.cleandoc(
            f"""
            <script>
            $(document).ready( function () {{
            var myTable = $('#{datatable_id}').DataTable({settings_str});
            {yadcf_script}
            }} );
            </script>
            """
        )

        settings = Settings(
            page=dict(
                # the following needs to be loaded in the header of the page, not the footer
                # this enables activating the tables in the body
                javascript=javascript_settings,
                css=css_settings,
            )
        )

        self._body = SpacedText(body_html, (2, 2))
        self._back = SpacedText(back_html, (2, 2)) + comment_ids(datatable_id)
        self._settings = settings


def _create_col_settings_tabulator(
    df: pd.DataFrame,
    add_header_filters: bool,
    prettify_colnames: bool,
    col_settings: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    # produce the column settings
    col_set_dict = {}
    for colname in df.columns:
        assert isinstance(colname, str)
        inner_dict: Dict[str, Any] = {"field": colname}
        if add_header_filters:
            # depending on the type of the column, choose a different filter
            filter_dict = _series_to_filter_tabulator(df[colname])
            inner_dict.update(filter_dict)
        if prettify_colnames:
            inner_dict["title"] = snake_to_text(colname)
        else:
            inner_dict["title"] = colname
        col_set_dict[colname] = inner_dict
    col_set_dict = merge_settings(
        col_set_dict, col_settings if col_settings is not None else {}
    )

    col_list = list(col_set_dict.values())
    return col_list


def _series_to_filter_tabulator(series: pd.Series) -> Dict[str, Any]:
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
            headerFilter=func_ref("minMaxFilterEditor"),
            headerFilterFunc=func_ref("minMaxFilterFunction"),
            headerFilterLiveFilter=False,
        )
    return dict(headerFilter="input")


@register_md("Tabulator")
class Tabulator(File):
    """A table using the Tabulator javascript library."""

    def __init__(
        self,
        table: pd.DataFrame,
        page_info: PageInfo,
        max_rows: Optional[int] = 1000,
        table_settings: Optional[dict] = None,
        add_header_filters: bool = True,
        prettify_colnames: bool = True,
        col_settings: Optional[dict] = None,
        downloads: bool = False,
        table_kwargs: Optional[dict] = None,
    ):
        """

        Args:
            table (pd.DataFrame): The table to be added.
            page_info (PageInfo): PageInfo for the page where the table should be added.
            max_rows (Optional[int]): Maximum number of rows. If None, all will
                be included. If longer, a warning will be logged and the first `max_rows`
                will be included.
            table_settings (Optional[dict]): Settings passed to Tabulator as json. Overrides
                any internal settings created by this function.
            add_header_filters (bool): Should header-filters be added.
            prettify_colnames (bool): Run column names through *snake_to_text*.
            col_settings (Optional[dict]): Column settings for tabulator, passed
                as json to the Tabulator library. Overrides any internal settings created.
            downloads (bool): Add download options.
            table_kwargs (Optional[dict]): Keyword args for the table
                when serializing to json.
        """
        assert page_info.idstore is not None
        assert page_info.page_path is not None
        assert page_info.javascript_path is not None

        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("tabulator.json")
            # here we use the split method; the index and columns
            # are not useful, but the rest gets set as 'data', which we need
            if max_rows is not None and table.shape[0] > max_rows:
                logger.warning(
                    f"Table has {table.shape[0]} rows, but only {max_rows} allowed. Truncating."
                )
                table = table.iloc[0:max_rows]
            table.to_json(
                path,
                orient="records",
                default_handler=str,
                **(table_kwargs if table_kwargs is not None else {}),
            )

            # Make sure the file is moved to the right place
            super().__init__(
                path=path, page_info=page_info, allow_copy=True, use_hash=True
            )

        # produce the column settings
        col_list = _create_col_settings_tabulator(
            table,
            add_header_filters=add_header_filters,
            prettify_colnames=prettify_colnames,
            col_settings=col_settings if col_settings is not None else {},
        )

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

        used_ids = []
        used_ids.append(tabulator_id := page_info.idstore.next_id("tabulator_id"))
        body_html = inspect.cleandoc(
            f"""
            <div id='{tabulator_id}' class='display'> </div>
            """
        )

        rel_table_path = relpath_html(self.path, page_info.page_path)
        table_settings = copy.deepcopy(self.table_settings)
        table_settings["ajaxURL"] = str(rel_table_path)

        # here we have to be careful to remove the '' around
        # the minMaxFilter function reference
        settings_str = serialize_json(table_settings)

        back_html = inspect.cleandoc(
            f"""
            <script>
            var table = new Tabulator('#{tabulator_id}', {settings_str});
            </script>
            """
        )

        javascript_settings = [
            "https://unpkg.com/tabulator-tables@5.1.0/dist/js/tabulator.min.js",
        ]
        css_settings = [
            "https://unpkg.com/tabulator-tables@5.1.0/dist/css/tabulator.min.css"
        ]

        if add_header_filters:
            javascript_settings.append(
                store_asset_relpath(Path("min_max_filter.js"), page_info)
            )

        if downloads:
            # add the necessary things to enable downloads
            # to the body
            used_ids.append(csv_down_id := page_info.idstore.next_id("csv_down_id"))
            used_ids.append(json_down_id := page_info.idstore.next_id("json_down_id"))
            used_ids.append(xlsx_down_id := page_info.idstore.next_id("xslx_down_id"))
            body_html = body_html + inspect.cleandoc(
                f"""
                    <div>
                      <button class="tabulator-btn-dwn", id="{csv_down_id}">to CSV</button>
                      <button class="tabulator-btn-dwn", id="{json_down_id}">to JSON</button>
                      <button class="tabulator-btn-dwn", id="{xlsx_down_id}">to XLSX</button>
                    </div>
                    """
            )
            # to the back_html
            split_back_html = back_html.split("\n")
            split_back_html.insert(
                -1,
                inspect.cleandoc(
                    f"""
                    //trigger download of data.csv file
                    $("#{csv_down_id}").click(function(){{
                        table.download("csv", "data.csv");
                    }});

                    //trigger download of data.json file
                    $("#{json_down_id}").click(function(){{
                        table.download("json", "data.json");
                    }});

                    //trigger download of data.xlsx file
                    $("#{xlsx_down_id}").click(function(){{
                        table.download("xlsx", "data.xlsx", {{sheetName:"data"}});
                    }});
                    """
                ),
            )
            back_html = "\n".join(split_back_html)
            # to the settings
            javascript_settings.append(
                "https://oss.sheetjs.com/sheetjs/xlsx.full.min.js"
            )
            css_settings.append(
                store_asset_relpath(Path("download_buttons.css"), page_info)
            )

        settings = Settings(
            page=dict(
                # the following needs to be loaded in the header of the page, not the footer
                # this enables activating the tables in the body
                javascript=javascript_settings,
                css=css_settings,
            )
        )

        self._body = SpacedText(body_html, (2, 2))
        self._back = SpacedText(back_html, (2, 2)) + "\n".join(
            [str(comment_ids(this_id)) for this_id in used_ids]
        )
        self._settings = settings
