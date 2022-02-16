---
{}
---

```python title="quickstart.py"
import pandas as pd
import plotnine as p9
from mkreports import Report
from plotnine.data import mtcars


def do_quickstart(report: Report) -> None:
    p = report.page("quickstart")

    p.H1("Quickstart")

    p.P(
        """
        First, below the code that was used to create this page. 
        It is a very brief example of an page with a table and an image
        as well as some text, like here.
        """
    )

    p.CodeFile(__file__)

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


if __name__ == "__main__":
    report = Report.create("mkreports_docs", report_name="Mkreports documentations")
    do_quickstart(report)

```
