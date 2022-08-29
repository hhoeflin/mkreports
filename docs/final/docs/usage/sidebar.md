---
css:
- ../../javascript/assets/code_admonition.css
hide:
- toc
---


??? code "Code"

    ```python title="docs/staging/sidebar.py"
    --8<-- 'docs/usage/sidebar/sidebar-4eaf9eb2a6c09580ff86f321534aa255.py'
    ```

# Sidebars

We can hide the table of contents sidebar as 
well as the navigation bar. On this page, we only hide the ToC.
When hiding the navigation bar, you should think about
setting navigation tabs as well (otherwise there is no direct navigation
option. 

Below a code block showing how to hide the ToC, Nav and set
the navigations tabs.


```python

p.HideToc()
p.HideNav()
p.NavTabs()

```
