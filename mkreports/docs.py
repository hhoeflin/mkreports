from pathlib import Path
from typing import Union

from .report import Report
from .settings import NavEntry, path_to_nav_entry


def add_pkg_docs(
    pkg_path: Path,
    parent_name: Union[NavEntry, Path, str],
    report: Report,
    omit_package_name: bool = False,
):
    """
    Add docstrings of the object to the report
    """
    # we need the parent name as a nav_entry
    if isinstance(parent_name, str):
        parent_name = Path(parent_name)
    if isinstance(parent_name, Path):
        parent_name = path_to_nav_entry(parent_name)

    # now iterate through all python entries
    for path in sorted(pkg_path.glob("**/*.py")):
        module_path = path.relative_to(pkg_path.parent).with_suffix("")
        if module_path.name.startswith("_"):
            continue
        else:
            if omit_package_name:
                nav_module_path = Path(*module_path.parts[1:])
            else:
                nav_module_path = module_path

            # now create the new nav_entry for this page
            module_nav_entry = NavEntry(
                tuple(parent_name[0]) + tuple(nav_module_path.parts),
                (parent_name[1] / nav_module_path).with_suffix(".md"),
            )

            # now create a new page and add the doc-entry
            page = report.page(module_nav_entry, truncate=True)
            page.add(page.md.Docstring(".".join(module_path.parts)))
