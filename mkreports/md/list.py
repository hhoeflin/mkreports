from typing import Iterable, Literal, Sequence, Union

from .base import MdObj, MdSeq, Raw
from .md_proxy import register_md
from .text import SpacedText, Text


def indent_hanging(x: str, hanging: str, spaces: int = 4):
    x_lines = x.split("\n")
    x_lines[0] = hanging + x_lines[0]

    if len(x_lines) > 1:
        for i in range(1, len(x_lines)):
            x_lines[i] = " " * spaces + x_lines[i]

    return "\n".join(x_lines)


@register_md("List")
class List(MdObj):
    marker: Literal["-", "*", "+", "1"]
    list: MdSeq

    def __init__(
        self,
        items: Union[str, Iterable[Union[MdObj, str]]] = (),
        marker: Literal["-", "*", "+", "1"] = "-",
    ):
        super().__init__()
        self.list = MdSeq(items)
        self.marker = marker

        # create the markdown output for every item; indent it appropriately
        # and then put it all together.

        self._back = None
        self._settings = None

    @property
    def body(self):
        # now we need to attach the right element at the beginning
        if self.marker == "1":
            prefix = [f"{i}. " for i in range(len(self))]
        else:
            prefix = [f"{self.marker} "] * len(self)

        md_list = [
            indent_hanging(elem.body.text, hanging=prefix)
            for elem, prefix in zip(self.list.items, prefix)
        ]

        return SpacedText("\n".join(md_list), (2, 2))

    def append(self, item: Union[Text, MdObj]) -> "List":
        if isinstance(item, (str, SpacedText)):
            item = Raw(item)
        return List(self.list.items + (item,), marker=self.marker)

    def extend(self, items: Sequence[Union[Text, MdObj]]) -> "List":
        items = tuple(
            [
                Raw(item) if isinstance(item, (str, SpacedText)) else item
                for item in items
            ]
        )
        return List(self.list.items + items, marker=self.marker)

    def __len__(self) -> int:
        return len(self.list)

    def __add__(self, other) -> "List":
        del other
        raise NotImplementedError("Addition not supported for MdList")

    def __radd__(self, other) -> "List":
        del other
        raise NotImplementedError("Addition not supported for MdList")
