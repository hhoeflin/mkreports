# Adding markdown elements to a page

## Opening pages

The first step is to define a *report* directory and open a page in it.
There is always at least the 'index.md' page included in any report,
which is listed in the navigation under *Home*.

```python
from mkreports import Report

report = Report()
page = report.page('index.md')
```

## Adding markdown

There are overall 3 ways to use and add markdown elements to a page.
Each of these provides a different level of convenient. As a summary
for the user:
- If you want to add an element immediately to a page, use the markdown
  classes directly available as attributes in the page itself. These
  preset certain parameters and add the markdown object directly to the
  page after it is instantiated.
- If you need to build up more complicated markdown objects before adding
  it to a page (e.g. in the case of nested objects), use the `Page.md` attribute
  to get the markdown object that pre-populates certain parameters to
  sensible defaults
- In some special circumstances it may be necessary to get the raw markdown
  with full control. In this case the `mkreports.md` module can be used.

In more detail below the three options, in reverse order from most basic to
most convenient.

### md module

The `mkreports.md` module provides all markdown functionality that
can be used in the package. In the rest of this documentation, various
of these are being explained. As the most basic there is however certain
information that can get cumbersome to input. One example is
the `store_path`. Certain markdown elements, such as tables, store
the information to be displayed in a file in subdirectory of
the reports directory. As the page on which the markdown element is added
is not specified at this point (and neither is the report), this `store_path`
needs to be explicitly passed into the element. For most use-cases, this
basic level does not need to be used by the end-user.

This markdown object then has to be added to a page using the `add` method.

### md-attribute of a page

Each `Page` instance also `md` attribute. This attribute is a proxy-object
to the `md`-submodule. When requesting an object, the `store_path` and certain
required `ids` (e.g. for Altair or DataTable objects) will be pre-populated
by the `page` instance so that the user doesn't have to worry about it.

The resulting markdown object then has to be added to the page again using
the `add` method.

### Markdown attributes of a page

This is very similar to the `Page.md` attribute, except that the markdown
classes are directly available as attributes on the `Page` class. After instantiating
the markdown element, it immediately gets added to the page automatically.
Keyword parameters that are available on `Page.add` can also be specified and will
be passed along appropriately.
