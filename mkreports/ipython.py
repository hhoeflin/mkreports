import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, Union

from IPython.core.magic import Magics, line_magic, magics_class

from . import md
from .report import Page, Report


@dataclass
class Handler:
    name: str
    class_type: Union[type, Tuple[type, ...]]
    func: Callable
    add_code: bool


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
            self.report = Report(
                os.environ["MKREPORTS_DIR"], site_name="Mkreports console", create=True
            )
            self.open_console()
        else:
            raise Exception("No 'MKREPORTS_DIR' in environment")

    def _set_default_handlers(self):
        self.handlers = []
        # handler for tables
        try:
            import pandas as pd

            self.handlers.append(
                Handler(
                    name="datatable",
                    class_type=pd.DataFrame,
                    func=lambda x: self.console.md.DataTable(x),
                    add_code=True,
                )
            )
        except Exception:
            pass

        # handler for matplotlib
        try:
            from matplotlib.figure import Figure as MplFigure

            self.handlers.append(
                Handler(
                    name="matplotlib",
                    class_type=MplFigure,
                    func=lambda x: self.console.md.Image(x),
                    add_code=True,
                )
            )
        except Exception:
            pass

        try:
            from plotnine.ggplot import ggplot

            self.handlers.append(
                Handler(
                    name="plotnine",
                    class_type=ggplot,
                    func=lambda x: self.console.md.Image(x),
                    add_code=True,
                )
            )
        except Exception:
            pass

        try:
            from seaborn import FacetGrid as SnsFacetGrid
            from seaborn import JointGrid as SnsJointGrid
            from seaborn import PairGrid as SnsPairGrid

            self.handlers.append(
                Handler(
                    name="seaborn",
                    class_type=(SnsFacetGrid, SnsJointGrid, SnsPairGrid),
                    func=lambda x: self.console.md.Image(x),
                    add_code=True,
                )
            )

        except Exception:
            pass

        self.handlers.append(
            Handler(name="mdobj", class_type=md.MdObj, func=lambda x: x, add_code=False)
        )

    def get_handler(self, obj: Any) -> Optional[Handler]:
        for handler in self.handlers:
            if isinstance(obj, handler.class_type):
                return handler
        else:
            return None

    def open_console(self) -> None:
        self.console = self.report.get_page((["Console"], Path("console/index.md")))
        # make sure the table of contents does not get shown
        self.console.add(
            md.Raw(
                page_settings={"hide": ["toc"]},
                mkdocs_settings={"theme": {"features": ["navigation.indexes"]}},
            )
        )

    @line_magic
    def archive_console(self, line):
        """
        Function to archive the console. This is also a line magic, however
        the line itself will be ignored.
        """
        print(line)
        # we also need to add a navigation entry
        new_entry = ["Console", f"{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}.md"]
        new_path = (
            self.console.path.parent / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        # we move teh page out of the way
        shutil.move(
            self.console.path,
            new_path,
        )
        self.report._add_nav_entry((new_entry, new_path))
        self.open_console()

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
            handler = self.get_handler(result.result)
            if handler is not None:
                md_obj = handler.func(result.result)

                if handler.add_code:
                    # we now want to attach this together with the stored code
                    content = md.Tab(md_obj, title="Content")
                    code = md.Tab(
                        md.Code("\n".join(self.stored_code), language="python"),
                        title="Code",
                    )
                    md_obj = content + code

                # and we also want a separator and a date
                post = (
                    md.H6(f"{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
                    + md_obj
                    + md.Raw(md.SpacedText("---", (2, 2)))
                )
                self.console.add(post, add_code=False, bottom=False)
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
    from . import md

    cw.shell.push({"md": md, "cons": cw.console})
    ip.events.register("post_run_cell", cw.post_run_cell)
    ip.register_magics(cw)
