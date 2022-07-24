# Purpose of the project

## Introduction

For data analysts, the output of a project is typically a
report of the derived results of the dataset, be it
an algorithm, the summary of a regression model and the significance
of variables or some other sort of requested insight.

In order to simplify the writing of such reports, various tools
have been invented, the most well known ones being
[RMarkdown](https://rmarkdown.rstudio.com/) in *R*
and [Jupyter](https://jupyter.org/)
that is mostly used with Python (but supports many other
languages as well).

These tools are incarnations of a *Literate Programming*,
that had its beginnings with tools such as
[noweb](https://www.cs.tufts.edu/~nr/noweb/) and aims to mix regular text
with code in an article, but of course that have been developed much further
since then to extend to interactively editing and running code such as in Jupyter,
processing entire books (see e.g. [bookdown](https://www.bookdown.org/) or
also inverting the text and code-blocks such that the regular text becomes
comments inside a script in e.g. R or Python (see
[jupytext][jupytext]).


## Jupyter and related tools

As this package is only for Python, I will focus in the following on
aspects of these tools for this language, but some comments are certainly
also valid for other frameworks.

*Jupyter* is for sure the most used framework for this purpose with a
very large set of tools and users. Since its invention, it has certainly
changed how datascience is being done in many organizations. Some of its
most noteworthy advantages are:
- Deployment through the browser without the need of direct access to hardware.
  Due to this it is also simpler to have users work with on-demand resources
- A good console with outputs of tables and figures that make rapid development easy
- Tools such as turning jupyter notebooks into websites
- Jupyterlab, which is (almost) a full Python IDE

Next to these positive sides are however also a few shortcomings.

## Shortcomings of Jupyter

One of the side-effects of structure of Jupyter-notebooks is their linear
form where code and output blocks are mixed, which can cause notebooks to become
very large and particular places can be hard to find. Code sharing between notebooks
is also not easily possible, requiring to write libraries outside the notebook
to fulfill this purpose, mixing very different styles of coding.

Also related to their design of one notebook, one html page, parametrization of
notebooks can be cumbersome and is certainly not as simple and straightforward as
a function.

## This package

This package was developed to give an alternative to Jupyter providing
more sophisticated ways to create reports while retaining (some) of the
interactivity of the browser. All this will be done in pure python without
any specially formatted file or overloading of the meaning of any comments.

It will further retain the ability to include live code-blocks from the
scripts in the output, but less intrusively than for Jupyter notebooks.

In particular, it is intended to work by providing functions to easily
write out markdown pages that are part of an mkdocs site. For this
convenience functions for Figures and Tables as well as other objects are
available.

For viewing these results, mkdocs is used that contains a development
server that automatically watches input files and updates the browser on
any change. This update process is typically very fast.

Last, a plugin for the ipython console is provided that writes
any appropriate output in the console to a special markdown page
that can then also be viewed using mkdocs. This way, it is easy
to visualize figues and tables from the ipython console, where
tables in the browser are sortable or can even be filtered, thus
providing better functionality than default Jupyter tables in an
output cell.

[jupytext]: https://jupytext.readthedocs.io/en/latest/
