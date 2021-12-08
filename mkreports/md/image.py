import hashlib
import shutil
import tempfile
from copy import copy
from pathlib import Path
from typing import Literal, Optional

from mdutils.tools.Image import Image as UtilsImage

from .base import MdObj
from .text import SpacedText


def md5_hash_file(path: Path) -> str:
    m = hashlib.md5()
    with path.open("rb") as f:
        m.update(f.read())

    return m.hexdigest()


def relpath(path_to, path_from):
    path_to = Path(path_to).absolute()
    path_from = Path(path_from).absolute()
    head = Path("/")
    tail = Path("")
    try:
        for p in (*reversed(path_from.parents), path_from):
            head, tail = p, path_to.relative_to(p)
    except ValueError:  # Stop when the paths diverge.
        pass
    return Path("../" * (len(path_from.parents) - len(head.parents))).joinpath(tail)


class File(MdObj):

    path: Path
    relative_to: Optional[Path]

    def __init__(
        self,
        path: Path,
        store_path: Path,
        allow_copy: bool = True,
        hash: bool = False,
    ) -> None:
        super().__init__()
        self.path = path.absolute()

        self.allow_copy = allow_copy
        self.hash = hash
        self.store_path = store_path

        if self.allow_copy:

            if self.hash:
                # we calculate the hash of the file to be ingested
                path_hash = md5_hash_file(self.path)
                new_path = store_path / (
                    self.path.stem + "-" + path_hash + self.path.suffix
                )
            else:
                new_path = store_path / self.path.name

            # now see if we move or copy the file
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.path, new_path)
            self.path = new_path
        else:
            new_file = self

    def to_markdown(self, page_path: Optional[Path] = None) -> SpacedText:
        return SpacedText("")


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
        img_type=Literal["jpg", "png"],
    ) -> None:
        if type(image) in image_save_funcs:
            # ok, we know how to save this: put it in temp dir first
            with tempfile.TemporaryDirectory() as dir:
                path = Path(dir) / "img." + img_type
                image_save_funcs[type(image)](
                    image=image,
                    path=path,
                    width=width,
                    height=height,
                    dpi=dpi,
                    units=units,
                )
            # now we create the ImageFile object
            super().__init__(
                path=path,
                store_path=store_path,
                link_type=link_type,
                text=text,
                tooltip=tooltip,
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
