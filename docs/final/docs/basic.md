---
{}
---


# Basic formatting elements

## Headings[](){:name='my-headings'}

```python title="Available headings"

md.H1("Header type 1")
md.H2("Header type 2")
md.H3("Header type 3")
md.H4("Header type 4")
md.H5("Header type 5")
md.H6("Header type 6")
md.H7("Header type 7")

```

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

    ```python title="basic.py" linenums="28"
    numbered_list = (
        md.List(marker="1")
        .append("First item")
        .append("Second item")
        .append("Third item")
    )
    unordered_list = md.List(("apples", "pears", "strawberry"), marker="*")

    numbered_list = numbered_list.append(
        md.Raw("Some fruit:") + unordered_list
    ).append(
        md.Raw("A code block:")
        + md.Code(
            """
            print("Hello world")                    
            """,
            title="Hello world",
            language="python",
        ),
    )

    ```

## Links

A number of different types of links are possible. Those within
a page to an anchor or to another page (with or without anchor)

=== "Content"

    A link back to the [first heading](#my-headings)

    A link to another page [Images](images.md)

    Or just to any page [Google](https://google.com)

    Or of course also just straight markdown [Google](https://google.com)

=== "Code"

    ```python title="basic.py" linenums="59"
    x = md.P(
        "A link back to the "
        + md.Link(anchor=heading_anchor, text="first heading")
    )
    x += md.P(
        "A link to another page "
        + md.Link("Images", to_page_path=report.page("images.md").path)
    )
    x += md.P(
        "Or just to any page " + md.Link("Google", url="https://google.com")
    )
    x += md.P(
        "Or of course also just straight markdown [Google](https://google.com)"
    )

    ```
