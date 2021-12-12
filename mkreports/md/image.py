import tempfile
from pathlib import Path
from typing import Literal, Optional

from mdutils.tools.Image import Image as UtilsImage

from .file import File, relpath
from .text import SpacedText


class ImageFile(File):
    def __init__(
        self,
        path: Path,
        store_path: Path,
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
        store_path: Path,
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
