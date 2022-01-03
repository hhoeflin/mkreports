import inspect
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Union

from mdutils.tools.Image import Image as UtilsImage
from mkreports.settings import Settings

from .file import File, relpath, true_stem
from .text import SpacedText


class ImageFile(File):
    text: str
    tooltip: str
    link_type: str

    def __init__(
        self,
        path: Union[str, Path],
        store_path: Optional[Path] = None,
        link_type: Literal["inline", "ref"] = "inline",
        text: str = "",
        tooltip: str = "",
        allow_copy: bool = True,
        use_hash: bool = True,
    ) -> None:
        super().__init__(
            path=path, store_path=store_path, allow_copy=allow_copy, use_hash=use_hash
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
                    use_hash=True,
                )
        else:
            raise ValueError("Unsupported image type")


class Altair(File):
    def __init__(
        self,
        altair,
        store_path: Optional[Path] = None,
        altair_id: Optional[str] = None,
        **kwargs,
    ):
        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("altair.csv")
            # here we use the split method; the index and columns
            # are not useful, but the rest gets set as 'data', which we need
            with path.open("w") as f:
                f.write(altair.to_json(**kwargs))

            # Make sure the file is moved to the rigth place
            super().__init__(
                path=path, store_path=store_path, allow_copy=True, use_hash=True
            )

        # use the hashed table name as the id if there is no other
        if altair_id is None:
            altair_id = true_stem(self.path)
        self.altair_id = altair_id

    def req_settings(self):
        settings = Settings(
            page=dict(
                # the following needs to be loaded in the header of the page, not the footer
                # this enables activating the tables in the body
                javascript=[
                    "https://cdn.jsdelivr.net/npm/vega@5",
                    "https://cdn.jsdelivr.net/npm/vega-lite@5",
                    "https://cdn.jsdelivr.net/npm/vega-embed@6",
                ],
            )
        )
        return settings

    def to_markdown(self, page_path: Path):
        if page_path is None:
            raise ValueError(
                "page_path must be set for relative referencing of json data file."
            )

        # now we insert the data table on the page
        # note: as we are inserting directly into html, we have to do one addition
        # level deeper for the relative path
        rel_spec_path = str(relpath(self.path, page_path))
        raw_html = inspect.cleandoc(
            f"""
            <div id='{self.altair_id}'> </div>
            <script>
                vegaEmbed("#{self.altair_id}", "{rel_spec_path}")
    	        // result.view provides access to the Vega View API
                .then(result => console.log(result))
                .catch(console.warn);
            </script>
            """
        )

        return SpacedText(raw_html, (2, 2))


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
        image.save(
            path,
            width=width,
            height=height,
            dpi=dpi,
            units=units,
            verbose=False,
            **kwargs,
        )

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
