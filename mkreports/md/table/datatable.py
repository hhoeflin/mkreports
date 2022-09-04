import inspect
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Set

import attrs
import pandas as pd
from pandas.api import types

from mkreports.md.base import RenderedMd, comment_ids, func_kwargs_as_set
from mkreports.md.file import File, relpath_html
from mkreports.md.idstore import IDStore
from mkreports.md.md_proxy import register_md
from mkreports.md.settings import Settings, merge_settings
from mkreports.md.text import SpacedText
from mkreports.utils import serialize_json, snake_to_text

logger = logging.getLogger(__name__)


def _create_yadcf_settings_datatable(
    df: pd.DataFrame,
    yadcf_settings: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
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
    return col_set_dict


def _series_to_filter_yadcf(series: pd.Series) -> Dict[str, Any]:
    if types.is_bool_dtype(series.dtype):  # type: ignore
        return dict(
            filter_type="select",
        )
    if types.is_categorical_dtype(series.dtype):  # type: ignore
        return dict(
            filter_type="select",
        )
    if types.is_numeric_dtype(series.dtype):  # type: ignore
        return dict(
            filter_type="range_number",
        )
    return dict(filter_type="text")


@register_md("DataTable")
@attrs.mutable()
class DataTable(File):
    """
    Initialize the table using the DataTable javascript library.

    Args:
        table (pd.DataFrame): The table in pandas.DataFrame format.
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
        json_name (str): Name of the saved file (before hash if hash=True)
        use_hash (bool): Should the name of the copied image be updated with a hash (Default: True)
    """

    table: pd.DataFrame
    column_settings: Optional[dict]
    prettify_colnames: bool
    add_header_filters: bool
    yadcf_settings: Dict[str, Dict[str, Any]]
    downloads: bool
    user_table_settings: Optional[dict]

    def __init__(
        self,
        table: pd.DataFrame,
        max_rows: Optional[int] = 1000,
        column_settings: Optional[dict] = None,
        prettify_colnames: bool = True,
        add_header_filters: bool = False,
        yadcf_settings: Optional[dict] = None,
        table_kwargs: Optional[dict] = None,
        downloads: bool = False,
        table_settings: Optional[dict] = None,
        json_name: str = "datatable",
        use_hash: bool = True,
    ):

        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / (f"{json_name}.json")
            # here we use the split method; the index and columns
            if max_rows is not None and table.shape[0] > max_rows:
                logger.warning(
                    f"Table has {table.shape[0]} rows, but only {max_rows} allowed. Truncating."
                )
                table = table.iloc[0:max_rows]
            # are not useful, but the rest gets set as 'data', which we need
            table.to_json(  # type: ignore
                path,
                orient="split",
                default_handler=str,
                **(table_kwargs if table_kwargs is not None else {}),
            )

            DataTable.__attrs_init__(  # type: ignore
                self,
                table=table,
                column_settings=column_settings,
                prettify_colnames=prettify_colnames,
                add_header_filters=add_header_filters,
                yadcf_settings=yadcf_settings if yadcf_settings is not None else {},
                downloads=downloads,
                user_table_settings=table_settings,
                path=path,
                allow_copy=True,
                use_hash=use_hash,
            )

    def _render(  # type: ignore
        self, page_asset_dir: Path, idstore: IDStore, page_path: Path
    ) -> RenderedMd:
        super()._render(page_asset_dir=page_asset_dir)

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
        if self.prettify_colnames:
            col_set = {
                col: {"title": snake_to_text(col) if isinstance(col, str) else col}
                for col in self.table.columns
            }
        else:
            col_set = {col: {"title": col} for col in self.table.columns}
        if self.column_settings is not None:
            # only pick out settings for columns that occur in the table
            col_set.update(
                {col: self.column_settings[col] for col in self.table.columns}
            )

        if self.add_header_filters:
            self.yadcf_settings = _create_yadcf_settings_datatable(
                self.table,
                self.yadcf_settings if self.yadcf_settings is not None else {},
            )

        # put together the settings for the table
        # there, the columns are a list in the correct order
        self.table_settings = {
            "scrollX": "true",
            "columns": [col_set[col] for col in self.table.columns],
        }

        if self.downloads:
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

        datatable_id = idstore.next_id("datatable_id")
        body_html = inspect.cleandoc(
            f"""
            <table id='{datatable_id}' class='display' style='width:100%'> </table>
            """
        )

        rel_table_path = relpath_html(self.path, page_path)
        self.table_settings["ajax"] = str(rel_table_path)
        # overwrite with given settigns if necessary
        self.table_settings.update(
            self.user_table_settings if self.user_table_settings is not None else {}
        )
        settings_str = serialize_json(self.table_settings)

        # prepare the header script if necessary
        if self.add_header_filters:
            yadcf_settings_str = serialize_json(list(self.yadcf_settings.values()))
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

        body = SpacedText(body_html, (2, 2))
        back = SpacedText(back_html, (2, 2)) + comment_ids(datatable_id)
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return func_kwargs_as_set(self._render)
