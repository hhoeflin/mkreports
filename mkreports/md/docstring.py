from typing import Set

from .base import MdObj, RenderedMd
from .md_proxy import register_md
from .settings import Settings
from .text import SpacedText


@register_md("Docstring")
class Docstring(MdObj):
    """Add a docstring to the page."""

    def __init__(self, obj_name: str) -> None:
        """
        Docstring for the page.

        Args:
            obj_name (str): Name of the object for which a docstring should be added.
        """
        super().__init__()
        self.obj_name = obj_name

    def _render(self) -> RenderedMd:
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
