from .base import MdObj
from .md_proxy import register_md
from .settings import Settings
from .text import SpacedText


@register_md("Docstring")
class Docstring(MdObj):
    """Add a docstring to the page."""

    def __init__(self, obj_name: str) -> None:
        super().__init__()
        self.obj_name = obj_name

        cont_settings = Settings(
            mkdocs={
                "plugins": [
                    "search",
                    "mkdocstrings",
                ]
            }
        )
        self._body = SpacedText(f"::: {self.obj_name}", (2, 2))
        self._back = None
        self._settings = cont_settings
