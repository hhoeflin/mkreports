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

### Markdown attributes of a page

All markdown objects are available under their name directory for a
`Page` object (created from a `Report`). For these, all parameters related to
a page and project are captured in a single parameter `page_info` that expects
and object of type `PageInfo` with names:

- `store_path`
- `page_path`
- `report_path`
- `project_root`
- `javascript_path`
- `idstore`

When requesting a markdown object from a page, this is automatically added.
The object is immediately added to the page.

A list of all available object can be obtained with

```python
page.md.proxied_classes
```

where `page` is a `Page` and the returned object is a dict of all registered
markdown objects. The key of the dict is the name under which it is available
as an attribute from the page.

### `md` attribute of a `Page`

Each `Page` instance also has a `md` attribute. These expose the markdown
object same as explained above, except that they will not be added to the page.
This would have to be done manually. This is sometimes useful if more
complex nested objects need to be created (e.g. for lists).

### md module

Also available is the `mkreports.md` module. These are the base objects
with no parameters pre-filled. This is only intended for experts that need
special behavior that is not covered by the regular `Page` object.
