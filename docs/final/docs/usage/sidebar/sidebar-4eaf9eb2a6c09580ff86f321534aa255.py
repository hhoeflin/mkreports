from mkreports import Report


def use_sidebar(report: Report) -> None:
    p = report.page("usage/sidebar", truncate=True)

    p.CollapsedCodeFile(__file__)
    p.H1("Sidebars")
    p.P(
        """
        We can hide the table of contents sidebar as 
        well as the navigation bar. On this page, we only hide the ToC.
        When hiding the navigation bar, you should think about
        setting navigation tabs as well (otherwise there is no direct navigation
        option. 

        Below a code block showing how to hide the ToC, Nav and set
        the navigations tabs.
        """
    )

    p.HideToc()

    p.Code(
        """
        p.HideToc()
        p.HideNav()
        p.NavTabs()
        """
    )
