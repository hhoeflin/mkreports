---
css:
- ../javascript/code_admonition.css
hide:
- toc
---


??? code "Code"

    ```python title="docs/staging/sidebar.py"
    --8<-- 'docs/sidebar_store/sidebar-c3de7d2a4f5e337b1c14f39615cf55b1.py'
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
