"""A package to programmatically create mkdocs sites."""

__version__ = "0.7.2"

from .config import Config
from .docs import add_pkg_docs
from .ipython import load_ipython_extension
from .page import Page
from .report import Report
from .settings import NavEntry
from .utils import relative_repo_root

__all__ = [
    "add_pkg_docs",
    "load_ipython_extension",
    "Page",
    "Report",
    "NavEntry",
    "relative_repo_root",
    "Config",
]
