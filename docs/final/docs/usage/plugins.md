# Creating custom plugins

All objects in this package that are used to add markdown (or html) to
a page are all created using a plugin system. This enables other people
to easily create their own `MdObj` objects and register them with `mkreports`
so that they behave exactly as all other objects shipped with this package.

Essentially, only 2 steps are needed:

1. Create a new class that inherits from `MdObj`. There are many examples
    available in this package on how to do that. Especially interesting
    examples are the tables as well as images, but also `HideNav`, `HideToc`
    and `NavTabs` as they show how to use settings.

2. Register the new class. This is easily done using the `register_md` decorator,
    which takes as its only argument the name under which the new class should
    be registered.


After this is done, all classes are available as attributes on a `Page` as well
as in `Page.md` with `page_info` parameters pre-set with the appropriate `PageInfo`
object.
