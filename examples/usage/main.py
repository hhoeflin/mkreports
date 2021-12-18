from pathlib import Path

import matplotlib.pyplot as plt
from mkreports import Report, md
from plotnine import aes, facet_wrap, geom_point, ggplot, stat_smooth
from plotnine.data import mtcars


def use_images(report: Report) -> None:
    """
    Show all different ways on how we can include images.
    """
    p = report.get_page("images.md", append=False)

    p.add(md.H1("Using images"))
    p.add(md.H2("Supported formats"))
    p.add(
        """
        Mkreports supports inclusion out of the box of a number of different imaging 
        libraries. For each supported library, an example is show below.

        For any not supported library, it is still possible to write out the 
        image manually and then include it as an `ImageFile` object.
        """
    )

    p.add(md.H3("Matplotlib"))

    p.add(
        """
        For many scientific graphing purposes, `matplotlib` is either the direct
        choice or the backend being used for plotting. 
        """
    )

    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    p.add(md.Image(fig, store_path=p.gen_asset_path))

    p.add(md.H3("Plotnine"))

    p.add(
        """
        Any plots created by `plotnine` can be included directly. The code below
        is from the beginner example of the library.
        """
    )

    p.add(
        md.Image(
            ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
            + geom_point()
            + stat_smooth(method="lm")
            + facet_wrap("~gear"),
            store_path=p.gen_asset_path,
        )
    )

    p.add(md.H3("Seaborn"))
    p.add(md.Admonition("Still to be implemented", kind="warning"))

    p.add(md.H3("Altair"))
    p.add(md.Admonition("Still to be implemented", kind="warning"))

    p.add(md.H2("Different image sizes"))
    p.add(md.Admonition("Still to be implemented", kind="warning"))


if __name__ == "__main__":
    report = Report(Path("usage"), site_name="Mkreports documentations")
    # documentation for images
    use_images(report)
