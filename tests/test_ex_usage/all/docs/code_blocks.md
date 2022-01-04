---
{}
---


# Code blocks

## Tracking code

One of the features of mkreports is that we can include
code right from the script into the output. Not only does
this include the code block in the script itself, but
also the source of functions that are called in the block. 
Here as an example, the fibonacci sequence. 

This is enabled by the `track_code` method that is part of 
a page object and functions as a context manager which installs
a tracing function, recording
the code and all called functions and their source code. 

A code block that has been tracked can then be included
when adding a markdown object to a page by usig the 
`add_code=True` parameter. This is then combined with 
the markdown object by adding tabs (the markdown object 
active under the 'Content' tab and the code block under 'Code').

=== "Content"

    fib(3) = 2

=== "Code"

    === "&lt;main&gt;"

        ```python title="/home/hhoeflin/projects/mkreports/tests/examples/usage/code_blocks.py" linenums="43"
        x = 3
        a = fib(x)

        ```

    === "fib"

        ```python title="/home/hhoeflin/projects/mkreports/tests/examples/usage/code_blocks.py" linenums="4"
        def fib(n):
            if n == 0:
                return 0
            elif n == 1:
                return 1
            else:
                return fib(n - 1) + fib(n - 2)

        ```

## Relative to position

In addition to tracking code as shown above, we can also
refer to code blocks as either 
- the context around the current statement
- A number of statements around the current one. 

!!! warning

    This is not yet implemented
