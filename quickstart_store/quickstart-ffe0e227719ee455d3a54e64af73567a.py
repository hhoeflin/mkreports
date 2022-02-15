import pandas as pd
import plotnine as p9
from mkreports import Report
from plotnine.data import mtcars


def use_quickstart(report: Report) -> None:
    p = report.page("quickstart")

    p.H1("Quickstart")

    p.CollapsedCodeFile(__file__)

    p.P(
        """
        We are quickly analyzing the mtcars dataset 
        that is included with plotnine.
            """
    )

    with p.H2("Data as a table"):

        p.Tabulator(mtcars, add_header_filters=True, prettify_colnames=True)

    with p.H2("Some simple plots"):

        p.Image(
            (
                p9.ggplot(mtcars, p9.aes("wt", "mpg", color="factor(gear)"))
                + p9.geom_point()
                + p9.stat_smooth(method="lm")
                + p9.facet_wrap("~gear")
            )
        )
