---
css:
- ../javascript/code_admonition.css
---


# Code blocks

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

    ```python title="docs/staging/code_blocks.py" linenums="21"
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

    ```python title="docs/staging/code_blocks.py" linenums="52"
    p.P("The code as a collapsed admonition before the output.")
    x = 4
    a = fib(x)

    p.P(f"fib({x}) = {a}")


    ```

The code as a collapsed admonition before the output.fib(4) = 3

---

## Tracking code (top-o)

```python title="docs/staging/code_blocks.py" linenums="59"
p.P("The code as an open code block before the output.")
x = 5
a = fib(x)

p.P(f"fib({x}) = {a}")


```

The code as an open code block before the output.fib(5) = 5

---

## Tracking code (bottom-c)
The code as a collapsed admoniton after the output.fib(6) = 8

??? code "Code"

    ```python title="docs/staging/code_blocks.py" linenums="66"
    p.P("The code as a collapsed admoniton after the output.")
    x = 6
    a = fib(x)

    p.Raw(f"fib({x}) = {a}")


    ```

---

## Tracking code (bottom-o)
The code as an open code block after the output.fib(7) = 13

```python title="docs/staging/code_blocks.py" linenums="73"
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

        ```python
        --8<-- 'docs/code_blocks_store/code_blocks-7cb6ac68f48f685a15dec6fd973a1c3f.py'
        ```

=== "Code"

    ```python title="docs/staging/code_blocks.py" linenums="80"
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

