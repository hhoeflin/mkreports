import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from IPython.core.magic import Magics, line_magic, magics_class  # type: ignore

from . import md
from .code_context import do_layout
from .config import get_mkreports_dir
from .md.handler import Handler, create_default_handlers, get_handler
from .report import Page, Report


@magics_class
class ConsoleWriter(Magics):
    """
    Class that connects IPython with mkreports using magics.
    """

    handlers: List[Handler]
    console: Page

    def __init__(self, ip):
        """Initialization. Not for end-users."""
        super().__init__(ip)
        self.shell = ip
        self.handlers = []
        self.stored_code = []

        # identify an mkreport
        self.report = Report.create(
            get_mkreports_dir(),
            report_name="Mkreports console",
            exist_ok=True,
        )
        self._open_console()
        self._set_default_handlers()

    def _set_default_handlers(self):
        self.handlers = create_default_handlers(self.console.md)

    def _get_handler(self, obj: Any) -> Optional[Handler]:
        return get_handler(obj, self.handlers)

    def _open_console(self) -> None:
        self.console = self.report.page(Path("console/active.md"), add_bottom=False)
        # make sure the table of contents does not get shown
        self.console.HideToc()

    @line_magic
    def archive_console(self, line):
        """
        Function to archive the console. This is also a line magic, however
        the line itself will be ignored.

        Args:
            line (str): ignored.
        """
        del line
        # we also need to add a navigation entry
        new_entry = ["Console", f"{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"]
        new_path = (
            self.console.path.parent / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        # we move the page out of the way
        shutil.move(
            str(self.console.path),
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
