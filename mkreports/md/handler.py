"""Handlers for MdObj in Ipython."""
from contextlib import suppress
from typing import Any, Callable, List, Optional, Tuple, Union

import attrs

from .base import MdObj
from .md_proxy import MdProxy


@attrs.mutable()
class Handler:
    """
    A handler for output.

    Args:
        name (str): Name of the handler.
        class_type (Union[type, Tuple[type, ...]]): Classes covered by the handler.
        func (Callable): the function to use to handle the output.
    """

    name: str
    class_type: Union[type, Tuple[type, ...]]
    func: Callable


def create_default_handlers(md_ns: MdProxy) -> List[Handler]:
    """
    Create default handlers for the IPython integration.

    Args:
        md_ns (MdProxy): Namespace with MdObj classes to handle.

    Returns:
        List of handler objects.

    """
    handlers = []
    with suppress(ImportError):
        import pandas as pd

        handlers.append(
            Handler(
                name="datatable",
                class_type=pd.DataFrame,
                func=lambda *args, **kwargs: md_ns.DataTable(*args, **kwargs),
            )
        )

    handlers.append(Handler(name="mdobj", class_type=MdObj, func=lambda x: x))

    handlers.extend(create_image_handlers(md_ns))

    return handlers


def get_handler(obj: Any, handler_list: List[Handler]) -> Optional[Handler]:
    """
    Get a fitting handler from a list of handlers.

    Args:
        obj (Any): The object for which we want the handler.
        handler_list (List[Handler]): List of available handlers.

    Returns:
        The handler to use, or None if there isn't one.

    """
    for handler in handler_list:
        if isinstance(obj, handler.class_type):
            return handler
    else:
        return None


def create_image_handlers(md_ns: MdProxy) -> List[Handler]:
    """
    Create handlers for images.

    Args:
        md_ns (MdProxy): The namespace for which to create handlers.

    Returns:
        List of created handlers.

    """
    handlers = []

    with suppress(ImportError):
        from PIL.Image import Image as PILImage

        handlers.append(
            Handler(
                name="PIL",
                class_type=PILImage,
                func=lambda *args, **kwargs: md_ns.PIL(*args, **kwargs),
            )
        )
    # handler for matplotlib
    with suppress(ImportError):
        from matplotlib.figure import Figure as MplFigure  # type: ignore

        handlers.append(
            Handler(
                name="matplotlib",
                class_type=MplFigure,
                func=lambda *args, **kwargs: (md_ns.Matplotlib)(*args, **kwargs),
            )
        )

    with suppress(ImportError):
        from plotnine.ggplot import ggplot  # type: ignore

        handlers.append(
            Handler(
                name="plotnine",
                class_type=ggplot,
                func=lambda *args, **kwargs: (md_ns.Plotnine)(*args, **kwargs),
            )
        )

    with suppress(ImportError):
        from seaborn import FacetGrid as SnsFacetGrid  # type: ignore
        from seaborn import JointGrid as SnsJointGrid
        from seaborn import PairGrid as SnsPairGrid

        handlers.append(
            Handler(
                name="seaborn",
                class_type=(SnsFacetGrid, SnsJointGrid, SnsPairGrid),
                func=lambda *args, **kwargs: (md_ns.Seaborn)(*args, **kwargs),
            )
        )

    with suppress(ImportError):
        from altair import Chart  # type: ignore

        handlers.append(
            Handler(
                name="altair",
                class_type=Chart,
                func=lambda *args, **kwargs: (md_ns.Altair)(*args, **kwargs),
            )
        )

    with suppress(ImportError):
        from plotly.graph_objs import Figure as PlotlyFigure  # type: ignore

        handlers.append(
            Handler(
                name="plotly",
                class_type=PlotlyFigure,  # type: ignore
                func=lambda *args, **kwargs: (md_ns.Plotly)(*args, **kwargs),
            )
        )
    return handlers
