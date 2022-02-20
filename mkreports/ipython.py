import os
import shutil
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, Union

from IPython.core.magic import Magics, line_magic, magics_class

from . import md
from .code_context import do_layout
from .report import Page, Report


@dataclass
class Handler:
    """
    A handler for output.

    Args:
        name (str): Name of the handler.
        class_type (Union[type, Tuple[type, ...]]): Classes covered by the handler.
        func (Callable): the function to use to handle the output.
    """

    name: str
    class_type: Union[type, Tuple[type, ...]]
    func: Callable


@magics_class
class ConsoleWriter(Magics):
    handlers: List[Handler]
    console: Page

    def __init__(self, ip):
        super().__init__(ip)
        self.shell = ip
        self.handlers = []
        self.stored_code = []
        self._set_default_handlers()

        # identify an mkreport
        if "MKREPORTS_DIR" in os.environ:
            self.report = Report.create(
                os.environ["MKREPORTS_DIR"],
                report_name="Mkreports console",
                exist_ok=True,
            )
            self._open_console()
        else:
            raise Exception("No 'MKREPORTS_DIR' in environment")

    def _set_default_handlers(self):
        self.handlers = []
        # handler for tables
        with suppress(ImportError):
            import pandas as pd

            self.handlers.append(
                Handler(
                    name="datatable",
                    class_type=pd.DataFrame,
                    func=lambda x: self.console.md.DataTable(x),
                )
            )

        # handler for matplotlib
        with suppress(ImportError):
            from matplotlib.figure import Figure as MplFigure

            self.handlers.append(
                Handler(
                    name="matplotlib",
                    class_type=MplFigure,
                    func=lambda x: self.console.md.Image(x),
                )
            )

        with suppress(ImportError):
            from plotnine.ggplot import ggplot

            self.handlers.append(
                Handler(
                    name="plotnine",
                    class_type=ggplot,
                    func=lambda x: self.console.md.Image(x),
                )
            )

        with suppress(ImportError):
            from seaborn import FacetGrid as SnsFacetGrid
            from seaborn import JointGrid as SnsJointGrid
            from seaborn import PairGrid as SnsPairGrid

            self.handlers.append(
                Handler(
                    name="seaborn",
                    class_type=(SnsFacetGrid, SnsJointGrid, SnsPairGrid),
                    func=lambda x: self.console.md.Image(x),
                )
            )

        self.handlers.append(
            Handler(name="mdobj", class_type=md.MdObj, func=lambda x: x)
        )

    def _get_handler(self, obj: Any) -> Optional[Handler]:
        for handler in self.handlers:
            if isinstance(obj, handler.class_type):
                return handler
        else:
            return None

    def _open_console(self) -> None:
        self.console = self.report.page(Path("console/active.md"), add_bottom=False)
        # make sure the table of contents does not get shown
        self.console.HideToc()

    @line_magic
    def archive_console(self, line):
        """
        Function to archive the console. This is also a line magic, however
        the line itself will be ignored.
        """
        del line
        # we also need to add a navigation entry
        new_entry = ["Console", f"{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"]
        new_path = (
            self.console.path.parent / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        # we move the page out of the way
        shutil.move(
            self.console.path,
            new_path,
        )
        self.report._add_nav_entry((new_entry, new_path))
        self._open_console()

    def post_run_cell(self, result):
        """
        Print any results of certain classes automatically to the console.

        Here we set some defaults so that results of certain classes are
        automatically written to the console, mostly data tables and images.
        These will then also have the corresponding code attached to them.
        """
        if result.success:
            # we store the cell content
            self.stored_code.append(result.info.raw_cell)
            handler = self._get_handler(result.result)
            if handler is not None:
                content = handler.func(result.result)
                code = md.Code("\n".join(self.stored_code), language="python")

                code_content = do_layout(
                    code=code,
                    content=content,
                    layout=self.console.code_layout,
                    page_info=self.console.page_info,
                )
                # and we also want a separator and a date
                post = (
                    md.H6(f"{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
                    + code_content
                )
                self.console.add(post)
                self.stored_code = []


def load_ipython_extension(ip):
    """
    Loading of the IPython Extension.

    Identify the report to use and
    export a page representing the console to use.

    Also insert handlers that automatically send appropriate results
    to be appended to the console. The console object should be part
    of the user-space, same as the markdown module for use.
    """
    cw = ConsoleWriter(ip)

    cw.shell.push({"md": cw.console.md, "cons": cw.console})
    ip.events.register("post_run_cell", cw.post_run_cell)
    ip.register_magics(cw)
