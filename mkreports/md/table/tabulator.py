import copy
import inspect
import logging
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional, Set

import attrs
import pandas as pd
from pandas.api import types

from mkreports.md.base import RenderedMd, comment_ids, func_kwargs_as_set
from mkreports.md.file import File, relpath_html, store_asset_relpath
from mkreports.md.idstore import IDStore
from mkreports.md.md_proxy import register_md
from mkreports.md.settings import Settings, merge_settings
from mkreports.md.text import SpacedText
from mkreports.utils import func_ref, serialize_json, snake_to_text

logger = logging.getLogger(__name__)


def _create_col_settings_tabulator(
    df: pd.DataFrame,
    add_header_filters: bool,
    prettify_colnames: bool,
    col_settings: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
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
    return col_set_dict


def _series_to_filter_tabulator(series: pd.Series) -> Dict[str, Any]:
    if types.is_bool_dtype(series.dtype):  # type: ignore
        return dict(
            headerFilter="tickCross",
            formatter="tickCross",
            headerFilterParams=dict(tristate=True),
        )
    if types.is_categorical_dtype(series.dtype):  # type: ignore
        return dict(
            headerFilter="select",
            headerFilterParams=dict(
                values=[""] + series.cat.categories.values.tolist(),  # type: ignore
            ),
        )
    if types.is_numeric_dtype(series.dtype):  # type: ignore
        return dict(
            width=80,
            headerFilter=func_ref("minMaxFilterEditor"),
            headerFilterFunc=func_ref("minMaxFilterFunction"),
            headerFilterLiveFilter=False,
        )
    return dict(headerFilter="input")


@register_md("Tabulator")
class Tabulator(File):
    """
    A table using the Tabulator javascript library.

    Args:
        table (pd.DataFrame): The table to be added.
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
        json_name (str): Name of the saved file (before hash if hash=True)
        use_hash (bool): Should the name of the copied image be updated with a hash (Default: True)
    """

    def __init__(
        self,
        table: pd.DataFrame,
        max_rows: Optional[int] = 1000,
        table_settings: Optional[dict] = None,
        add_header_filters: bool = True,
        prettify_colnames: bool = True,
        col_settings: Optional[dict] = None,
        downloads: bool = False,
        table_kwargs: Optional[dict] = None,
        json_name: str = "tabulator",
        use_hash: bool = True,
    ):
        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / (f"{json_name}.json")
            # here we use the split method; the index and columns
            # are not useful, but the rest gets set as 'data', which we need
            if max_rows is not None and table.shape[0] > max_rows:
                logger.warning(
                    f"Table has {table.shape[0]} rows, but only {max_rows} allowed. Truncating."
                )
                table = table.iloc[0:max_rows]
            table.to_json(  # type: ignore
                path,
                orient="records",
                default_handler=str,
                **(table_kwargs if table_kwargs is not None else {}),
            )
            self.table = deepcopy(table)

            # Make sure the file is moved to the right place
            super().__init__(path=path, allow_copy=True, use_hash=use_hash)
        self.user_table_settings = table_settings
        self.add_header_filters = add_header_filters
        self.prettify_colnames = prettify_colnames
        self.col_settings = col_settings
        self.downloads = downloads

    def _render(  # type: ignore
        self,
        idstore: IDStore,
        page_path: Path,
        report_asset_dir: Path,
        page_asset_dir: Path,
    ) -> RenderedMd:
        super()._render(page_asset_dir=page_asset_dir)
        # produce the column settings
        col_dict = _create_col_settings_tabulator(
            self.table,
            add_header_filters=self.add_header_filters,
            prettify_colnames=self.prettify_colnames,
            col_settings=self.col_settings if self.col_settings is not None else {},
        )

        # put the other settings together
        self.table_settings: Dict[str, Any] = merge_settings(
            dict(
                layout="fitDataTable",
                pagination=True,
                paginationSize=10,
                paginationSizeSelector=True,
            ),
            self.user_table_settings if self.user_table_settings is not None else {},
        )
        # the table settings expects a list; the column names are encoded in the settings as field
        self.table_settings["columns"] = list(col_dict.values())

        used_ids = []
        used_ids.append(tabulator_id := idstore.next_id("tabulator_id"))
        body_html = inspect.cleandoc(
            f"""
            <div id='{tabulator_id}' class='display'> </div>
            """
        )

        rel_table_path = relpath_html(self.path, page_path)
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

        if self.add_header_filters:
            javascript_settings.append(
                store_asset_relpath(
                    Path("min_max_filter.js"),
                    asset_dir=report_asset_dir,
                    page_path=page_path,
                )
            )

        if self.downloads:
            # add the necessary things to enable downloads
            # to the body
            used_ids.append(csv_down_id := idstore.next_id("csv_down_id"))
            used_ids.append(json_down_id := idstore.next_id("json_down_id"))
            used_ids.append(xlsx_down_id := idstore.next_id("xslx_down_id"))
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
                store_asset_relpath(
                    Path("download_buttons.css"),
                    asset_dir=report_asset_dir,
                    page_path=page_path,
                )
            )

        settings = Settings(
            page=dict(
                # the following needs to be loaded in the header of the page, not the footer
                # this enables activating the tables in the body
                javascript=javascript_settings,
                css=css_settings,
            )
        )

        body = SpacedText(body_html, (2, 2))
        back = SpacedText(back_html, (2, 2)) + "\n".join(
            [str(comment_ids(this_id)) for this_id in used_ids]
        )
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return func_kwargs_as_set(self._render)
