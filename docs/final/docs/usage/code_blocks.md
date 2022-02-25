---
css:
- ../../javascript/assets/code_admonition.css
---


# Code blocks

??? code "Code"

    ```python title="docs/staging/code_blocks.py" linenums="19"
    p.P(
        """
        Here we use nested trackers. The outer tracker uses a 
        'top-c' layout, so the code is a collapsed admonition at the top
        right above this paragraph.

        The other blocks below are nested inside this one.
        """
    )

    with p.H2("Tracking code (tabbed)"):
        p.Raw(
            """
            One of the features of mkreports is that we can include
            code right from the script into the output. This is done by 
            starting a context manager and all code in the 
            scope of the context manager will be recorded.
            """
        )

        x = 3
        a = fib(x)

        p.P(f"fib({x}) = {a}")

        p.P(
            """
            By default, the **tabbed** version will be used, but there
            are also the options

            - **top-c**: Collapsed code block at the top
            - **top-o**: Open code block at the top
            - **bottom-c**: Collapsed code block at the bottom
            - **bottom-o**: Open code block at the bottom

            The default style can be set when creating the page using the 
            `code_layout` parameter, but can also be set one at a time later
            using the `ctx` method on a page.
                """
        )

    with p.H2("Tracking code (top-c)").ctx(layout="top-c"):
        p.P("The code as a collapsed admonition before the output.")
        x = 4
        a = fib(x)

        p.P(f"fib({x}) = {a}")

    with p.H2("Tracking code (top-o)").ctx(layout="top-o"):
        p.P("The code as an open code block before the output.")
        x = 5
        a = fib(x)

        p.P(f"fib({x}) = {a}")

    with p.H2("Tracking code (bottom-c)").ctx(layout="bottom-c"):
        p.P("The code as a collapsed admoniton after the output.")
        x = 6
        a = fib(x)

        p.Raw(f"fib({x}) = {a}")

    with p.H2("Tracking code (bottom-o)").ctx(layout="bottom-o"):
        p.P("The code as an open code block after the output.")
        x = 7
        a = fib(x)

        p.P(f"fib({x}) = {a}")

    with p.H2("Adding code files"):
        p.P(
            """
            In addtion we can also add entire code files, for 
            example at the end of a page the file or files that 
            created a page. This can be wrapped into a collapsed
            admonition so that the file is hidden.
            """
        )

        p.CollapsedCodeFile(__file__)

    p.P(
        """
        And at the end will add another copy of the code-file, 
        but automatically when ending the page context manager.
        """
    )

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

    ```python title="docs/staging/code_blocks.py" linenums="30"
    p.Raw(
        """
        One of the features of mkreports is that we can include
        code right from the script into the output. This is done by 
        starting a context manager and all code in the 
        scope of the context manager will be recorded.
        """
    )

    x = 3
    a = fib(x)

    p.P(f"fib({x}) = {a}")

    p.P(
        """
        By default, the **tabbed** version will be used, but there
        are also the options

        - **top-c**: Collapsed code block at the top
        - **top-o**: Open code block at the top
        - **bottom-c**: Collapsed code block at the bottom
        - **bottom-o**: Open code block at the bottom

        The default style can be set when creating the page using the 
        `code_layout` parameter, but can also be set one at a time later
        using the `ctx` method on a page.
            """
    )


    ```

---

## Tracking code (top-c)

??? code "Code"

    ```python title="docs/staging/code_blocks.py" linenums="61"
    p.P("The code as a collapsed admonition before the output.")
    x = 4
    a = fib(x)

    p.P(f"fib({x}) = {a}")


    ```

The code as a collapsed admonition before the output.

fib(4) = 3

---

## Tracking code (top-o)

```python title="docs/staging/code_blocks.py" linenums="68"
p.P("The code as an open code block before the output.")
x = 5
a = fib(x)

p.P(f"fib({x}) = {a}")


```

The code as an open code block before the output.

fib(5) = 5

---

## Tracking code (bottom-c)

The code as a collapsed admoniton after the output.

fib(6) = 8

??? code "Code"

    ```python title="docs/staging/code_blocks.py" linenums="75"
    p.P("The code as a collapsed admoniton after the output.")
    x = 6
    a = fib(x)

    p.Raw(f"fib({x}) = {a}")


    ```

---

## Tracking code (bottom-o)

The code as an open code block after the output.

fib(7) = 13

```python title="docs/staging/code_blocks.py" linenums="82"
p.P("The code as an open code block after the output.")
x = 7
a = fib(x)

p.P(f"fib({x}) = {a}")


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
        --8<-- 'docs/usage/code_blocks_store/code_blocks-87ceafb80dd96b5cdb9d0a8f4e6aba17.py'
        ```

=== "Code"

    ```python title="docs/staging/code_blocks.py" linenums="89"
    p.P(
        """
        In addtion we can also add entire code files, for 
        example at the end of a page the file or files that 
        created a page. This can be wrapped into a collapsed
        admonition so that the file is hidden.
        """
    )

    p.CollapsedCodeFile(__file__)


    ```

---

And at the end will add another copy of the code-file, 
but automatically when ending the page context manager.

---
