---
css:
- ../../javascript/assets/code_admonition.css
---


# Basic formatting elements

??? code "Code"

    ```python title="docs/staging/basic.py"
    --8<-- 'docs/usage/basic_store/basic-e2790dcbcc97bebbab0872249f1c0d78.py'
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

    ```python title="docs/staging/basic.py" linenums="12"
    p.Code(
        """
        md.H1("Header type 1")
        md.H2("Header type 2")
        md.H3("Header type 3")
        md.H4("Header type 4")
        md.H5("Header type 5")
        md.H6("Header type 6")
        md.H7("Header type 7")
        """,
        title="Available headings",
    )


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

    ```python title="docs/staging/basic.py" linenums="26"
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

    p2.add(numbered_list)


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

    ```python title="docs/staging/basic.py" linenums="50"
    p2.Raw(
        """
        A number of different types of links are possible. Those within
        a page to an anchor or to another page (with or without anchor)
        """
    )
    p2.P(
        "A link back to the "
        + p.md.ReportLink(anchor=heading_anchor, text="first heading")
    )
    p2.P(
        "A link to another page "
        + p.md.ReportLink(
            "Images", to_page_path=report.page("usage/images.md").path
        )
    )
    p2.P("Or just to any page " + p.md.Link("Google", url="https://google.com"))
    p2.P("Or of course also just straight markdown [Google](https://google.com)")

    ```

---
