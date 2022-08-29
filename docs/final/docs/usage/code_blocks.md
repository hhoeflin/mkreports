---
css:
- ../../assets/assets/code_admonition.css
---


# Code blocks

??? code "Code"

    ```python title=".conda_env/lib/python3.8/site-packages/mkreports/page.py" linenums="157"
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        self.multi_code_context.__exit__(exc_type, exc_val, traceback)
        if self.multi_code_context.md_obj_after_finish is not None:

    ```

Here we use nested trackers. The outer tracker uses a 
'top-c' layout, so the code is a collapsed admonition at the top
right above this paragraph.

The other blocks below are nested inside this one.

## Tracking code (tabbed)

=== "Content"

    One of the features of mkreports is that we can include
    code right from the script into the output. This is done by 
    starting a context manager and all code in the 
    scope of the context manager will be recorded.

    fib(3) = 2

    By default, the **tabbed** version will be used, but there
    are also the options

    - **top-c**: Collapsed code block at the top
    - **top-o**: Open code block at the top
    - **bottom-c**: Collapsed code block at the bottom
    - **bottom-o**: Open code block at the bottom

    The default style can be set when creating the page using the 
    `code_layout` parameter, but can also be set one at a time later
    using the `ctx` method on a page.

=== "Code"

    ```python title=".conda_env/lib/python3.8/site-packages/mkreports/page.py" linenums="157"
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        self.multi_code_context.__exit__(exc_type, exc_val, traceback)
        if self.multi_code_context.md_obj_after_finish is not None:

    ```

---

## Tracking code (top-c)

??? code "Code"

    ```python title=".conda_env/lib/python3.8/site-packages/mkreports/page.py" linenums="157"
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        self.multi_code_context.__exit__(exc_type, exc_val, traceback)
        if self.multi_code_context.md_obj_after_finish is not None:

    ```

The code as a collapsed admonition before the output.

fib(4) = 3

---

## Tracking code (top-o)

```python title=".conda_env/lib/python3.8/site-packages/mkreports/page.py" linenums="157"
    return self

def __exit__(self, exc_type, exc_val, traceback) -> None:
    self.multi_code_context.__exit__(exc_type, exc_val, traceback)
    if self.multi_code_context.md_obj_after_finish is not None:

```

The code as an open code block before the output.

fib(5) = 5

---

## Tracking code (bottom-c)

The code as a collapsed admoniton after the output.

fib(6) = 8

??? code "Code"

    ```python title=".conda_env/lib/python3.8/site-packages/mkreports/page.py" linenums="157"
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        self.multi_code_context.__exit__(exc_type, exc_val, traceback)
        if self.multi_code_context.md_obj_after_finish is not None:

    ```

---

## Tracking code (bottom-o)

The code as an open code block after the output.

fib(7) = 13

```python title=".conda_env/lib/python3.8/site-packages/mkreports/page.py" linenums="157"
    return self

def __exit__(self, exc_type, exc_val, traceback) -> None:
    self.multi_code_context.__exit__(exc_type, exc_val, traceback)
    if self.multi_code_context.md_obj_after_finish is not None:

```

---

## Adding code files

=== "Content"

    In addtion we can also add entire code files, for 
    example at the end of a page the file or files that 
    created a page. This can be wrapped into a collapsed
    admonition so that the file is hidden.

    ??? code "Code"

        ```python title="docs/staging/code_blocks.py"
        --8<-- 'docs/usage/code_blocks/code_blocks-87ceafb80dd96b5cdb9d0a8f4e6aba17.py'
        ```

=== "Code"

    ```python title=".conda_env/lib/python3.8/site-packages/mkreports/page.py" linenums="157"
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        self.multi_code_context.__exit__(exc_type, exc_val, traceback)
        if self.multi_code_context.md_obj_after_finish is not None:

    ```

---

And at the end will add another copy of the code-file, 
but automatically when ending the page context manager.

---
