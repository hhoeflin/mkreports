import pandas as pd
from mkreports import Report, md
from plotnine.data import mtcars


def use_tables(report: Report) -> None:
    """
    Show all the different ways on how we can work with tables.
    """
    with report.page("tables.md", truncate=True) as p:
        p.H1("Different ways of handling tables")

        p.add(
            """
            Conveying information with tables is very important for 
            any type of report. Standard tables in markdown format 
            can be very useful for this for limited amout of data, but for 
            larger tables more sophisticated libraries are needed. 
            """
        )
        with p.H2("Markdown tables"):
            p.add(
                """
                Below an example of a regular markdown table. As it is very wide,
                horizontal scrolling is enabled by default. In addition, the number
                of rows is limited to 10 as there is no automatic paging available.
                """
            )
            p.add(md.Table(pd.DataFrame(mtcars).head(10), index=False))

        with p.H2("DataTable javascript library"):
            p.add(
                """
                Here the same table, but displayed using the 
                [DataTables](https://datatables.net/)  
                plugin. With this, we get automatic paging, searching as well as sorting
                by columns. 
                """
            )
            # and as a DataTable
            p.DataTable(pd.DataFrame(mtcars))

        with p.H2("Tabulator javascript library"):
            p.add(
                """
                This time, we use the [Tabulator](http://tabulator.info)
                library. A library with a lot of interesting 
                functionality. Currently limited support.
                """
            )
            p.Tabulator(
                pd.DataFrame(mtcars), add_header_filters=False, prettify_colnames=False
            )

            with p.H3("Header filters"):
                p.add(
                    """
                    We also can enable header filtering. For the datatypes

                    - numeric
                    - boolean
                    - categorical 
                    - str
                    
                    default filter options have been defined. Below
                    we create a table with various different data types
                    to show these functions.

                    The applied filters are

                    - Input filter for the names
                    - Range filter with min and max for age
                    - Select dropdown for hair color
                    - and checkbox for marital status
                    """
                )
                ex_table = pd.DataFrame(
                    [
                        {"name": "Alfred", "age": 30, "hair": "red", "married": True},
                        {"name": "Beate", "age": 50, "hair": "brown", "married": False},
                        {
                            "name": "Caro",
                            "age": 7,
                            "hair": "green",
                            "married": False,
                        },
                    ]
                )
                ex_table["hair"] = pd.Categorical(ex_table.hair)
                p.Tabulator(ex_table, add_header_filters=True, prettify_colnames=True)
        with p.H2("Notes"):
            p.add(
                """
                Internally, the tables are serialized to json so that 
                they can be displayed in the web-browser. For any types 
                that are non-native to json (e.g. Path-instances), as a
                default handler the `str` funtion is called. If this
                is not ok, please transform the table columns accordingly.
                """
            )
