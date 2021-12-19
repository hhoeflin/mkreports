from mkreports import Report, md
from plotnine.data import mtcars


def use_tables(report: Report) -> None:
    """
    Show all the different ways on how we can work with tables.
    """
    with report.get_page("tables.md", append=False) as p:
        p.add(md.H1("Different ways of handling tables"))

        with p.add(md.H2("Markdown tables")):
            p.add(md.Table(mtcars, index=False))

        with p.add(md.H2("DataTable javascript library")):
            # and as a DataTable
            p.add(md.DataTable(mtcars))
