# Using IPython

## The extension

The `mkreports` package also has an extension for IPython. Here,
we are referring to the console-application IPython, not a Jupyter
notebook (which were in the past also referred to as IPython notebooks).

IPython here is just a replacement for the python console, similar
to for example [bpython](https://bpython-interpreter.org/). The reason
we are using IPython is that it provides a plugin interface
that allows us to extend its functionality.

The key ability here is to have tables and images that are the results
of commands in the IPython console to be automatically piped to
a *Console* page in the mkdocs report.

## How to use it

In order to use the IPython extension, we have to
set the `MKREPORTS_DIR` environment variable
to the folder in which the mkdocs report will be stored.

Then we can start the IPython console and execute

```python
%load_ext mkreports
```

Then in a separate shell, we go the directory that is referred to in
`MKREPORTS_DIR` and run

```bash
mkdocs serve
```
and start a browser. Then we visit the *Console* subpage.

Now, for every table or image that we create in the console, it
will also be added to the *Console* page. Each entry will have a timestamp
and end with a horizontal line. The code executed in the console since
the last item was added will also be added as a tab. New entries will
be added to the top of the page (at the bottom, there are problems with
inadvertent scrolling).

In addition, there are variables `cons` and `md` added to the console.
The `cons` variable refers to the *Console* page and can be used
just like any other `report` page in `mkreports`. The `md` object is the
same as `cons.md`, just added for convenience, and can be used to
create `MdObj` instances. An `MdObj` instance that is the result of a code-block
will also automatically be added to the *Console* page.

### Layout

By default, content and code will be presented as tabs. However, it also
possible to choose other layouts. For the options, look to the section on
code-blocks. In order to set a different layout, do

```
cons.code_layout = 'top-o'
```
in the IPython console. This, for example, will create visible code-blocks above
the content.



### Archiving

Once the *Console* page gets too long and becomes slower on reload, run

```python
%archive_console
```

This will push the old *Console* page to a page with a time-stamp and
create a new empty page to use for new additions.
