from mkreports.md_proxy import register_md

from .base import MdObj, MdOut
from .settings import Settings
from .text import SpacedText


@register_md("Docstring")
class Docstring(MdObj):
    def __init__(self, obj_name: str) -> None:
        super().__init__()
        self.obj_name = obj_name

    def to_markdown(self, **kwargs) -> MdOut:
        del kwargs
        cont_settings = Settings(
            mkdocs={
                "plugins": [
                    "search",
                    "mkdocstrings",
                ]
            }
        )
        return MdOut(
            body=SpacedText(f"::: {self.obj_name}", (2, 2)), settings=cont_settings
        )
