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

In this reports we want to provide an easier way to create static
reports for data analysis. The main tool of choice in this space
are of course Jupyter notebooks which can also be converted to
static html files. So why another tool?

The main reason is that having to switch to jupyter
notebooks breaks a workflow
in common editors such as vim as they don't natively
support jupyter notebooks. This problem can somewhat be
alleviated by using packages such as `jupytext` that allow
for the seamless conversion between notebooks and python files.
The end results are ok but not quite satisfactory as
- One python file corresponds to one output document
  (which can get very long)
- Incremental execution is not possible
- Regular debuggers such as pudb are not supported well supported
- It does not solve the issue that in remote ssh development
  shells the viewing of graphics can be complicated
- The display options for code and complex tables are limited.
- Easily pass paramters to create reports. This is functionality
  that for Jupyter is provided by tools such as `papermill`, but
  can be much easier achieved in native python.

For this package, the planned features are:
- Simple and convenient ways to save and include graphics in markdown files
- Simple way to include tables in markdown files, also for more complicated
  javascript display options
- Include code that was run in the output. For this, we would like
  a tabbed style, so that the code is only visible when desired and not
  all the time.
- Include an option to write the local variables of a stacktrace.
- Use this functionality together with IPython console to get a running
  log of an analysis session.

Using the development server of `mkdocs`, live updates of sessions will be
possible, including live updates of long-running scripts.

## Packages used here

- `mkdocs`: A package to create static websites from markdown documents
  that provides many features and is the bases for this package.
- `mkdocs-material`: The material theme for mkdocs that implements
  some features that we are using.
- `mdutils`: A package that gives already many options to write out
  markdown from python and that this package uses internally.
