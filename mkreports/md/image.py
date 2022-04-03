import inspect
import tempfile
from contextlib import suppress
from copy import deepcopy
from pathlib import Path
from typing import List, Literal, Optional, Union

from mdutils.tools.Image import Image as UtilsImage

from .base import comment_ids
from .file import File, relpath_html
from .handler import Handler, get_handler
from .md_proxy import register_md
from .settings import PageInfo, Settings
from .text import SpacedText


@register_md("ImageFile")
class ImageFile(File):
    """An image file."""

    text: str
    tooltip: str
    link_type: str

    def __init__(
        self,
        path: Union[str, Path],
        page_info: PageInfo,
        link_type: Literal["inline", "ref"] = "inline",
        text: str = "",
        tooltip: str = "",
        allow_copy: bool = True,
        use_hash: bool = True,
    ) -> None:
        """

        Args:
            path (Union[str, Path]): Path to the image file.
            page_info (PageInfo): PageInfo object about the page. Added by page-wrapper
            link_type (Literal["inline", "ref"]): Link-type to use.
            text (str): Text shown if the image can't be displayed.
            tooltip (str): The tooltip shown when hovering over the image.
            allow_copy (bool): Should the image-file be copied to the store (Default: True)
            use_hash (bool): Should the name of the copied image be updated with a hash (Default: True)
        """
        super().__init__(
            path=path, page_info=page_info, allow_copy=allow_copy, use_hash=use_hash
        )
        self.text = text
        self.tooltip = tooltip
        self.link_type = link_type

        # page_info needs to be set
        assert page_info.page_path is not None

        if self.link_type == "inline":
            self._body = SpacedText(
                UtilsImage.new_inline_image(
                    text=self.text,
                    path=str(relpath_html(self.path, page_info.page_path.parent)),
                    tooltip=self.tooltip,
                )
            )
            self._back = None
            self._settings = None
        elif type == "ref":
            raise NotImplementedError()
        else:
            raise ValueError(f"Unknown type {self.link_type}")


@register_md("Matplotlib")
class Matplotlib(ImageFile):
    def __init__(
        self,
        image,
        page_info: PageInfo,
        width: Optional[float] = None,
        height: Optional[float] = None,
        units: Literal["in", "cm", "mm"] = "in",
        dpi: Optional[float] = None,
        link_type: Literal["inline", "ref"] = "inline",
        text: str = "",
        tooltip: str = "",
        img_type: Literal["jpg", "png"] = "png",
    ) -> None:
        """
        An image object for inclusion on a page.

        Args:
            image: The image to be included. Has to be supported by one of the handlers, which
                are Matplotlib, plotnine and seaborn.
            page_info (PageInfo): PageInfo for the page where the image should be included.
            width (Optional[float]): width of the image
            height (Optional[float]): height of the image
            units (Literal["in", "cm", "mm"]): units of the width and height
            dpi (Optional[float]): dpi of the image output.
            link_type (Literal["inline", "ref"]): Link-type to be used.
            text (str): The alternative text if the image is not available.
            tooltip (str): The tooltip to use when hovering over the image.
            img_type (Literal["jpg", "png"]): Type of the image to create during saving.
        """
        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("image." + img_type)
            # for matplotlib
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
            image.savefig(path, dpi="figure" if dpi is None else dpi)

            super().__init__(
                path=path,
                page_info=page_info,
                link_type=link_type,
                text=text,
                tooltip=tooltip,
                allow_copy=True,
                use_hash=True,
            )


@register_md("Seaborn")
class Seaborn(Matplotlib):
    def __init__(
        self,
        image,
        page_info: PageInfo,
        width: Optional[float] = None,
        height: Optional[float] = None,
        units: Literal["in", "cm", "mm"] = "in",
        dpi: Optional[float] = None,
        link_type: Literal["inline", "ref"] = "inline",
        text: str = "",
        tooltip: str = "",
        img_type: Literal["jpg", "png"] = "png",
    ) -> None:
        """
        An image object for inclusion on a page.

        Args:
            image: The image to be included. Has to be supported by one of the handlers, which
                are Matplotlib, plotnine and seaborn.
            page_info (PageInfo): PageInfo for the page where the image should be included.
            width (Optional[float]): width of the image
            height (Optional[float]): height of the image
            units (Literal["in", "cm", "mm"]): units of the width and height
            dpi (Optional[float]): dpi of the image output.
            link_type (Literal["inline", "ref"]): Link-type to be used.
            text (str): The alternative text if the image is not available.
            tooltip (str): The tooltip to use when hovering over the image.
            img_type (Literal["jpg", "png"]): Type of the image to create during saving.
        """

        super().__init__(
            image.figure,
            page_info=page_info,
            width=width,
            height=height,
            units=units,
            dpi=dpi,
            link_type=link_type,
            text=text,
            tooltip=tooltip,
            img_type=img_type,
        )


@register_md("Plotnine")
class Plotnine(ImageFile):
    def __init__(
        self,
        image,
        page_info: PageInfo,
        width: Optional[float] = None,
        height: Optional[float] = None,
        units: Literal["in", "cm", "mm"] = "in",
        dpi: Optional[float] = None,
        link_type: Literal["inline", "ref"] = "inline",
        text: str = "",
        tooltip: str = "",
        img_type: Literal["jpg", "png"] = "png",
    ) -> None:
        """
        An image object for inclusion on a page.

        Args:
            image: The image to be included. Has to be supported by one of the handlers, which
                are Matplotlib, plotnine and seaborn.
            page_info (PageInfo): PageInfo for the page where the image should be included.
            width (Optional[float]): width of the image
            height (Optional[float]): height of the image
            units (Literal["in", "cm", "mm"]): units of the width and height
            dpi (Optional[float]): dpi of the image output.
            link_type (Literal["inline", "ref"]): Link-type to be used.
            text (str): The alternative text if the image is not available.
            tooltip (str): The tooltip to use when hovering over the image.
            img_type (Literal["jpg", "png"]): Type of the image to create during saving.
        """

        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("image." + img_type)
            image.save(
                path,
                width=width,
                height=height,
                dpi=dpi,
                units=units,
                verbose=False,
            )
            # now we create the ImageFile object
            # which will also move it into the store
            super().__init__(
                path=path,
                page_info=page_info,
                link_type=link_type,
                text=text,
                tooltip=tooltip,
                allow_copy=True,
                use_hash=True,
            )


@register_md("PIL")
class PIL(ImageFile):
    """A PIL image for inclusion."""

    def __init__(
        self,
        image,
        page_info: PageInfo,
        link_type: Literal["inline", "ref"] = "inline",
        text: str = "",
        tooltip: str = "",
        img_type: Literal["jpg", "png"] = "png",
    ) -> None:
        """
        Create MdObj for PIL image.

        Args:
            image (PIL.Image.Image): an Image object from PIL
            page_info (PageInfo): PageInfo for the page where the image is to be included.
            link_type (Literal["inline", "ref"]): Link-type to use.
            text (str): Alternative text for the image.
            tooltip (str): Tooltip when hovering over the image.
            img_type (Literal["jpg", "png"]): File-type to use when saving the image.
        """
        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("pil_image." + img_type)
            image.save(path)
            # now we create the ImageFile object
            # which will also move it into the store
            super().__init__(
                path=path,
                page_info=page_info,
                link_type=link_type,
                text=text,
                tooltip=tooltip,
                allow_copy=True,
                use_hash=True,
            )


@register_md("Altair")
class Altair(File):
    """
    Include an Altair image.
    """

    def __init__(
        self,
        altair,
        page_info: PageInfo,
        **kwargs,
    ):
        """
        Create object to include an Altair image.

        Args:
            altair: An altair image.
            page_info (PageInfo): PageInfo to the page where it is to be included.
        """
        assert page_info.page_path is not None
        assert page_info.idstore is not None

        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("altair.csv")
            # here we use the split method; the index and columns
            # are not useful, but the rest gets set as 'data', which we need
            with path.open("w") as f:
                f.write(altair.to_json(**kwargs))

            # Make sure the file is moved to the rigth place
            super().__init__(
                path=path,
                page_info=page_info,
                allow_copy=True,
                use_hash=True,
            )

        # note; in the body we just insert the div.
        # The reason is that this part can be indented, e.g.
        # inside a tab. But then <script> content can be escaped, leading to errors for '=>'
        # so the script tag itself gets done in the backmatter

        altair_id = page_info.idstore.next_id("altair_id")
        body_html = inspect.cleandoc(
            f"""
            <div id='{altair_id}'> </div>
            """
        )

        rel_spec_path = str(relpath_html(self.path, page_info.page_path))
        back_html = inspect.cleandoc(
            f"""
            <script>
                vegaEmbed("#{altair_id}", "{rel_spec_path}")
    	        // result.view provides access to the Vega View API
                .then(result => console.log(result))
                .catch(console.warn);
            </script>
            """
        )
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

        self._body = SpacedText(body_html, (2, 2))
        self._back = SpacedText(back_html, (2, 2)) + comment_ids(altair_id)
        self._settings = settings


@register_md("Plotly")
class Plotly(File):
    """
    Plotly image as MdObj.
    """

    def __init__(
        self,
        plotly,
        page_info: PageInfo,
        **kwargs,
    ):
        """
        Initialize the Plotly MdObj.

        Args:
            plotly (): The plotly graph to plot.
            page_info (PageInfo): PageInfo to the page where it is to be included.
        """
        assert page_info.page_path is not None
        assert page_info.idstore is not None

        with tempfile.TemporaryDirectory() as dir:
            path = Path(dir) / ("plotly.json")
            # here we use the split method; the index and columns
            # are not useful, but the rest gets set as 'data', which we need
            with path.open("w") as f:
                f.write(plotly.to_json(**kwargs))

            # Make sure the file is moved to the rigth place
            super().__init__(
                path=path, page_info=page_info, allow_copy=True, use_hash=True
            )

        # note; in the body we just insert the div.
        # The reason is that this part can be indented, e.g.
        # inside a tab. But then <script> content can be escaped, leading to errors for '=>'
        # so the script tag itself gets done in the backmatter

        plotly_id = page_info.idstore.next_id("plotly_id")
        body_html = inspect.cleandoc(
            f"""
            <div id='{plotly_id}'> </div>
            """
        )

        rel_spec_path = str(relpath_html(self.path, page_info.page_path))
        back_html = inspect.cleandoc(
            f"""
            <script>
                fetch('{rel_spec_path}')
                    .then(function (response) {{
                        return response.json();
                    }})
                    .then(function (data) {{
                        doPlotly(data);
                    }})
                    .catch(function (err) {{
                        console.log('error: ' + err);
                    }});
                function doPlotly(plotlyJson) {{
                    Plotly.newPlot("{plotly_id}", {{
                        "data": plotlyJson["data"],
                        "layout": plotlyJson["layout"]
                    }})
                }}
            </script>
            """
        )

        settings = Settings(
            page=dict(
                # the following needs to be loaded in the header of the page, not the footer
                # this enables activating the tables in the body
                javascript=[
                    "https://cdn.plot.ly/plotly-2.8.3.min.js",
                ],
            )
        )

        self._body = SpacedText(body_html, (2, 2))
        self._back = SpacedText(back_html, (2, 2)) + comment_ids(plotly_id)
        self._settings = settings
