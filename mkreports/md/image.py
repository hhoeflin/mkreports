import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Literal, Optional, Union

from mdutils.tools.Image import Image as UtilsImage

from .file import File, relpath
from .text import SpacedText


class ImageFile(File):
    def __init__(
        self,
        path: Path,
        store_path: Optional[Path] = None,
        link_type: Literal["inline", "ref"] = "inline",
        text: str = "",
        tooltip: str = "",
        allow_copy: bool = True,
        hash: bool = True,
    ) -> None:
        super().__init__(
            path=path, store_path=store_path, allow_copy=allow_copy, hash=hash
        )
        self.text = text
        self.tooltip = tooltip
        self.link_type = link_type

    def to_markdown(self, page_path: Path) -> SpacedText:
        if page_path is None:
            raise ValueError("Page path cannot be None")
        if self.link_type == "inline":
            return SpacedText(
                UtilsImage.new_inline_image(
                    text=self.text,
                    path=str(relpath(self.path, page_path.parent)),
                    tooltip=self.tooltip,
                )
            )
        elif type == "ref":
            raise NotImplementedError()
        else:
            raise ValueError(f"Unknown type {self.link_type}")


class Image(ImageFile):
    def __init__(
        self,
        image,
        store_path: Optional[Path] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        units: Literal["in", "cm", "mm"] = "in",
        dpi: Optional[float] = None,
        link_type: Literal["inline", "ref"] = "inline",
        text: str = "",
        tooltip: str = "",
        img_type: Literal["jpg", "png"] = "png",
    ) -> None:
        if type(image) in image_save_funcs:
            # ok, we know how to save this: put it in temp dir first
            with tempfile.TemporaryDirectory() as dir:
                path = Path(dir) / ("image." + img_type)
                image_save_funcs[type(image)](
                    image=image,
                    path=path,
                    width=width,
                    height=height,
                    dpi=dpi,
                    units=units,
                )
                # now we create the ImageFile object
                # which will also move it into the store
                super().__init__(
                    path=path,
                    store_path=store_path,
                    link_type=link_type,
                    text=text,
                    tooltip=tooltip,
                    allow_copy=True,
                    hash=True,
                )
        else:
            raise ValueError("Unsupported image type")


image_save_funcs = dict()
# for plotnine
try:
    from plotnine.ggplot import ggplot

    def ggplot_save(
        image: ggplot,
        path: Path,
        width: Optional[float] = None,
        height: Optional[float] = None,
        dpi: Optional[float] = None,
        units: Literal["in", "cm", "mm"] = "in",
        **kwargs,
    ):
        image.save(path, width=width, height=height, dpi=dpi, units=units, **kwargs)

    image_save_funcs[ggplot] = ggplot_save
except Exception:
    pass

# for matplotlib
try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure as MplFigure

    def matplotlib_save(
        image: MplFigure,
        path: Path,
        width: Optional[float] = None,
        height: Optional[float] = None,
        dpi: Optional[float] = None,
        units: Literal["in", "cm", "mm"] = "in",
        **kwargs,
    ):
        # first we need to convert the units if given
        if width is not None or height is not None:
            if units != "in":
                if units == "cm":
                    factor = 1 / 2.54
                elif units == "mm":
                    factor = 1 / (10 * 2.54)
                else:
                    raise ValueError(
                        f"unit {units} not supported. Must be one of 'in', 'cm' or 'mm'."
                    )
                width = width * factor if width is not None else None
                height = height * factor if height is not None else None

            # if only one of the two is set, we infer the other
            if width is None and height is not None:
                old_width = image.get_figwidth()
                old_height = image.get_figheight()
                width = old_width * (height / old_height)
            elif width is not None and height is None:
                old_width = image.get_figwidth()
                old_height = image.get_figheight()
                height = old_height * (width / old_width)

            # now we set the new figure height, but on a copy of the figure
            image = deepcopy(image)
            image.set_size_inches(w=width, h=height)

        # save it
        image.savefig(path, dpi="figure" if dpi is None else dpi, **kwargs)

    image_save_funcs[MplFigure] = matplotlib_save

except Exception:
    pass

# seaborn; if seaborn loads we can assume so does matplotlib
try:
    from seaborn import FacetGrid as SnsFacetGrid
    from seaborn import JointGrid as SnsJointGrid
    from seaborn import PairGrid as SnsPairGrid

    def seaborn_save(
        image: Union[SnsFacetGrid, SnsJointGrid, SnsPairGrid],
        path: Path,
        width: Optional[float] = None,
        height: Optional[float] = None,
        dpi: Optional[float] = None,
        units: Literal["in", "cm", "mm"] = "in",
        **kwargs,
    ):
        matplotlib_save(
            image=image.figure,
            path=path,
            width=width,
            height=height,
            dpi=dpi,
            units=units,
            **kwargs,
        )

    image_save_funcs[SnsFacetGrid] = seaborn_save
    image_save_funcs[SnsJointGrid] = seaborn_save
    image_save_funcs[SnsPairGrid] = seaborn_save

except Exception:
    pass
