from contextlib import suppress
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple, Union

from .base import MdObj


@dataclass
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


def create_default_handlers(md_ns) -> List[Handler]:
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

    handlers.append(
        Handler(name="mdobj", class_type=MdObj, func=lambda x, *args, **kwargs: x)
    )

    handlers.extend(create_image_handlers(md_ns))

    return handlers


def get_handler(obj: Any, handler_list: List[Handler]) -> Optional[Handler]:
    for handler in handler_list:
        if isinstance(obj, handler.class_type):
            return handler
    else:
        return None


def create_image_handlers(md_ns) -> List[Handler]:
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
        from matplotlib.figure import Figure as MplFigure

        handlers.append(
            Handler(
                name="matplotlib",
                class_type=MplFigure,
                func=lambda *args, **kwargs: (md_ns.Matplotlib)(*args, **kwargs),
            )
        )

    with suppress(ImportError):
        from plotnine.ggplot import ggplot

        handlers.append(
            Handler(
                name="plotnine",
                class_type=ggplot,
                func=lambda *args, **kwargs: (md_ns.Plotnine)(*args, **kwargs),
            )
        )

    with suppress(ImportError):
        from seaborn import FacetGrid as SnsFacetGrid
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
        from altair import Chart

        handlers.append(
            Handler(
                name="altair",
                class_type=Chart,
                func=lambda *args, **kwargs: (md_ns.Altair)(*args, **kwargs),
            )
        )

    with suppress(ImportError):
        from plotly.graph_objs import Figure as PlotlyFigure

        handlers.append(
            Handler(
                name="plotly",
                class_type=PlotlyFigure,  # type: ignore
                func=lambda *args, **kwargs: (md_ns.Plotly)(*args, **kwargs),
            )
        )
    return handlers
