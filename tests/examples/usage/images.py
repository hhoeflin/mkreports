import matplotlib.pyplot as plt
import seaborn as sns
from mkreports import Report, md
from plotnine import aes, facet_wrap, geom_point, ggplot, stat_smooth
from plotnine.data import mtcars


def use_images(report: Report) -> None:
    """
    Show all different ways on how we can include images.
    """
    with report.get_page("images.md", append=False) as p:

        # we don't need an indentation for everything if we don't want
        p.add(md.H1("Images"))

        with p.add(md.H2("Supported formats")):
            p.add(
                """
                Mkreports supports inclusion out of the box of a number of different imaging 
                libraries. For each supported library, an example is show below.

                For any not supported library, it is still possible to write out the 
                image manually and then include it as an `ImageFile` object.
                """
            )

            with p.add(md.H3("Matplotlib")):
                with p.track_code():

                    p.add(
                        """
                        For many scientific graphing purposes, `matplotlib` is either the direct
                        choice or the backend being used for plotting. 
                        """
                    )

                    fig, ax = plt.subplots()
                    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
                p.add(md.Image(fig), add_code=True)

            with p.add(md.H3("Plotnine")):
                with p.track_code():
                    p.add(
                        """
                        Any plots created by `plotnine` can be included directly. The code below
                        is from the beginner example of the library.
                        """
                    )

                    pn_image = md.Image(
                        ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
                        + geom_point()
                        + stat_smooth(method="lm")
                        + facet_wrap("~gear"),
                    )
                p.add(pn_image, add_code=True)

            with p.add(md.H3("Seaborn")):
                with p.track_code():
                    p.add(
                        """
                        Another well known option is Seaborn. The interface is similar to the 
                        ones before. Under the hood, the `figure` attribute of the seaborn plot is 
                        accessed and saved in the same fashion as for matplotlib.
                        """
                    )

                    sns.set_theme(style="ticks")

                    # Load the example dataset for Anscombe's quartet
                    df = sns.load_dataset("anscombe")

                    # Show the results of a linear regression within each dataset
                    sea_img = md.Image(
                        sns.lmplot(
                            x="x",
                            y="y",
                            col="dataset",
                            hue="dataset",
                            data=df,
                            col_wrap=2,
                            ci=None,
                            palette="muted",
                            height=4,
                            scatter_kws={"s": 50, "alpha": 1},
                        ),
                    )
                p.add(sea_img, add_code=True)

            with p.add(md.H3("Altair")):
                with p.track_code():
                    import altair as alt
                    import pandas as pd

                    source = pd.DataFrame(
                        {
                            "a": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
                            "b": [28, 55, 43, 91, 81, 53, 19, 87, 52],
                        }
                    )

                    altair_chart = md.Altair(
                        alt.Chart(source)
                        .mark_bar()
                        .encode(x="a", y="b")
                        .properties(width=600)
                    )

                p.add(altair_chart, add_code=True)

            with p.add(md.H3("Plotly")):
                with p.track_code():
                    import plotly.express as px

                    fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
                p.add(p.md.Plotly(fig), add_code=True)

        with p.add(md.H2("Different image sizes")):
            p.add(md.Admonition("Still to be implemented", kind="warning"))
