from typing import Set

import attrs

from .base import MdObj, RenderedMd
from .md_proxy import register_md
from .settings import Settings
from .text import SpacedText


@register_md("Docstring")
@attrs.mutable()
class Docstring(MdObj):
    """
    Docstring for the page.

    Args:
        obj_name (str): Name of the object for which a docstring should be added.
    """

    obj_name: str

    def _render(self) -> RenderedMd:  # type: ignore
        settings = Settings(
            mkdocs={
                "plugins": [
                    "search",
                    "mkdocstrings",
                ]
            }
        )
        body = SpacedText(f"::: {self.obj_name}", (2, 2))
        back = None
        return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return set()
