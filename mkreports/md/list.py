import functools
from typing import Iterable, Literal, Sequence, Set, Union

from .base import MdObj, MdSeq, Raw, RenderedMd
from .md_proxy import register_md
from .settings import Settings
from .text import SpacedText, Text


def _indent_hanging(x: str, hanging: str, spaces: int = 4):
    x_lines = x.split("\n")
    x_lines[0] = hanging + x_lines[0]

    if len(x_lines) > 1:
        for i in range(1, len(x_lines)):
            x_lines[i] = " " * spaces + x_lines[i]

    return "\n".join(x_lines)


@register_md("List")
class List(MdObj):
    """
    Markdown list.
    """

    marker: Literal["-", "*", "+", "1"]
    list: MdSeq

    def __init__(
        self,
        items: Union[str, Iterable[Union[MdObj, str]]] = (),
        marker: Literal["-", "*", "+", "1"] = "-",
    ):
        """
        Initialize the list as a markdown object.

        Args:
            items (Union[str, Iterable[Union[MdObj, str]]]): List of items in the list.
            marker (Literal["-", "*", "+", "1"]): Marker to use for the list.
        """
        super().__init__()
        self.items = tuple(items)
        self.marker = marker

    def append(self, item: Union[Text, MdObj]) -> "List":
        """
        Append an item. This returns a new list, does not append to the old.

        Args:
            item (Union[Text, MdObj]): The item to append to the list.

        Returns:
            List: A list object with the new item appended.
        """
        if isinstance(item, (str, SpacedText)):
            item = Raw(item)
        return List(self.items + (item,), marker=self.marker)

    def extend(self, items: Sequence[Union[Text, MdObj]]) -> "List":
        """
        Extend the list by additional items.

        The old list will not be updated. A new one will be created.

        Args:
            items (Sequence[Union[Text, MdObj]]): The items with which to extend the list.

        Returns:
            List: A new list object

        """
        items = tuple(
            [
                Raw(item) if isinstance(item, (str, SpacedText)) else item
                for item in items
            ]
        )
        return List(self.items + items, marker=self.marker)

    @property
    def num_items(self) -> int:
        """
        Number of items in the list.

        Returns:
            int: Number of items in the list.
        """
        return len(self.items)

    def _render(self, **kwargs) -> RenderedMd:
        if len(self.items) == 0:
            return RenderedMd(
                body=SpacedText(""), back=SpacedText(""), settings=Settings(), src=self
            )
        else:
            # create the markdown output for every item; indent it appropriately
            # and then put it all together.

            # create the body
            # now we need to attach the right element at the beginning
            if self.marker == "1":
                prefix = [f"{i}. " for i in range(self.num_items)]
            else:
                prefix = [f"{self.marker} "] * self.num_items

            rendered_list = [elem.render(**kwargs) for elem in self.list]
            md_list = [
                _indent_hanging(elem.body.text, hanging=prefix)
                for elem, prefix in zip(rendered_list, prefix)
            ]

            body = SpacedText("\n".join(md_list), (2, 2))
            back = functools.reduce(
                lambda x, y: x + y, [elem.back for elem in rendered_list]
            )
            settings = functools.reduce(
                lambda x, y: x + y, [elem.settings for elem in rendered_list]
            )
            return RenderedMd(body=body, back=back, settings=settings, src=self)

    def render_fixtures(self) -> Set[str]:
        return self.list.render_fixtures()
