![Pytest](https://github.com/hhoeflin/mkreports/actions/workflows/pytest.yml/badge.svg)

# Mkreports package

## Introduction

The mkreports package makes it easy for you to write complex reports in mkdocs
including tables, graphics and programmatically defined output
using only python scripts. No Jupyter notebooks or workarounds such
as jupytext are needed.

This methods works seamlessly with complex codebases, encourages
modularity and re-useability of code.

Below is an example of a simple page. However, the documentation for this
package is also created with `mkreports`. The code can be found in the
[documentation](https://hhoeflin.github.io/mkreports/site_code/main/).

## Quickstart

It is very easy to create new reports and pages. Below an example that
creates a report in the `example_report` directory and creates one page
`quickstart` in which a table and a plot of some data is shown together
with the code used to create those items.

```python
import pandas as pd
import plotnine as p9
from mkreports import Report
from plotnine.data import mtcars

report = Report.create("example_report", report_name="Mkreports documentations")

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

```

Now change to the folder `example_report` and run

```bash
mkdocs serve
```

and go to that page. The report will be shown in the browser. As the development
server of mkdocs supports automatic reload, as you run code, it will update automatically.
This is particularly convenient when running the IPython extension for interactive
analyses.

## Why write this package?

First of all, because developing it is fun to do. It is a very nice challenge to provide
a user friendly interface that provides a lot of flexibility.

Another reason was to provide a highly modular and flexible way to create reports
in markdown that can contain fragments obtained in computation. The main tool in this
space is Jupyter Notebooks at the moment, but hopefully this tool can provide an
alternative in certain settings.

## Packages used here

- `mkdocs`: A package to create static websites from markdown documents
  that provides many features and is the bases for this package.
- `mkdocs-material`: The material theme for mkdocs that implements
  some features that we are using.
- `mdutils`: A package that gives already many options to write out
  markdown from python and that this package uses internally.
