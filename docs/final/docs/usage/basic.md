---
css:
- ../../assets/assets/code_admonition.css
---


# Basic formatting elements

??? code "Code"

    ```python title="docs/staging/basic.py"
    --8<-- 'docs/usage/basic/basic-488791be69d4bcbbb01cd32cf0a7f941.py'
    ```

## Headings[](){:name='anchor-0'}

[comment]: # (id: anchor-0)

=== "Content"

    ```python title="Available headings"

    md.H1("Header type 1")
    md.H2("Header type 2")
    md.H3("Header type 3")
    md.H4("Header type 4")
    md.H5("Header type 5")
    md.H6("Header type 6")
    md.H7("Header type 7")

    ```

=== "Code"

    ```python title=".conda_env/lib/python3.8/site-packages/mkreports/page.py" linenums="192"
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        self.multi_code_context.__exit__(exc_type, exc_val, traceback)
        if self.multi_code_context.md_obj_after_finish is not None:

    ```

---

## Lists

=== "Content"

    0. First item
    1. Second item
    2. Third item
    3. Some fruit:
    
        * apples
        * pears
        * strawberry
    4. A code block:
    
        ```python title="Hello world"
    
        print("Hello world")                    
    
        ```

=== "Code"

    ```python title=".conda_env/lib/python3.8/site-packages/mkreports/page.py" linenums="192"
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        self.multi_code_context.__exit__(exc_type, exc_val, traceback)
        if self.multi_code_context.md_obj_after_finish is not None:

    ```

---

## Links

=== "Content"

    A number of different types of links are possible. Those within
    a page to an anchor or to another page (with or without anchor)

    A link back to the [first heading](#anchor-0)

    A link to another page [Images](images.md)

    Or just to any page [Google](https://google.com)

    Or of course also just straight markdown [Google](https://google.com)

=== "Code"

    ```python title=".conda_env/lib/python3.8/site-packages/mkreports/page.py" linenums="192"
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        self.multi_code_context.__exit__(exc_type, exc_val, traceback)
        if self.multi_code_context.md_obj_after_finish is not None:

    ```

---
