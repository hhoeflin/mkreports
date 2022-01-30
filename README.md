![Pytest](https://github.com/hhoeflin/mkreports/actions/workflows/pytest.yml/badge.svg)

*This project is in very early status; all APIs can change at any point in time.*

# Mkdocs based data analysis reports

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
