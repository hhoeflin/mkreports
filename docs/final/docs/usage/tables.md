---
css:
- ../../javascript/assets/code_admonition.css
- https://cdn.datatables.net/1.11.3/css/jquery.dataTables.min.css
- https://cdn.jsdelivr.net/gh/vedmack/yadcf@332407eeacbda299e6253530e24c15041b270227/dist/jquery.dataTables.yadcf.css
- https://cdn.datatables.net/buttons/2.2.2/css/buttons.dataTables.min.css
- https://unpkg.com/tabulator-tables@5.1.0/dist/css/tabulator.min.css
- ../../javascript/assets/download_buttons.css
javascript:
- https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js
- https://cdn.datatables.net/1.11.3/js/jquery.dataTables.min.js
- https://cdn.jsdelivr.net/gh/vedmack/yadcf@332407eeacbda299e6253530e24c15041b270227/dist/jquery.dataTables.yadcf.js
- https://cdn.datatables.net/buttons/2.2.2/js/dataTables.buttons.min.js
- https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js
- https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/pdfmake.min.js
- https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/vfs_fonts.js
- https://cdn.datatables.net/buttons/2.2.2/js/buttons.html5.min.js
- https://cdn.datatables.net/buttons/2.2.2/js/buttons.print.min.js
- https://unpkg.com/tabulator-tables@5.1.0/dist/js/tabulator.min.js
- ../../javascript/assets/min_max_filter.js
- https://oss.sheetjs.com/sheetjs/xlsx.full.min.js
---


# Different ways of handling tables

??? code "Code"

    ```python title="docs/staging/tables.py"
    --8<-- 'docs/usage/tables_store/tables-1de6e59c7f2c203b4a7b452262c65704.py'
    ```

Conveying information with tables is very important for 
any type of report. Standard tables in markdown format 
can be very useful for this for limited amout of data, but for 
larger tables more sophisticated libraries are needed. 

## Markdown tables

=== "Content"

    Below an example of a regular markdown table. As it is very wide,
    horizontal scrolling is enabled by default. In addition, the number
    of rows is limited to 10 as there is no automatic paging available.

    | name              |   mpg |   cyl |   disp |   hp |   drat |    wt |   qsec |   vs |   am |   gear |   carb |
    |:------------------|------:|------:|-------:|-----:|-------:|------:|-------:|-----:|-----:|-------:|-------:|
    | Mazda RX4         |  21   |     6 |  160   |  110 |   3.9  | 2.62  |  16.46 |    0 |    1 |      4 |      4 |
    | Mazda RX4 Wag     |  21   |     6 |  160   |  110 |   3.9  | 2.875 |  17.02 |    0 |    1 |      4 |      4 |
    | Datsun 710        |  22.8 |     4 |  108   |   93 |   3.85 | 2.32  |  18.61 |    1 |    1 |      4 |      1 |
    | Hornet 4 Drive    |  21.4 |     6 |  258   |  110 |   3.08 | 3.215 |  19.44 |    1 |    0 |      3 |      1 |
    | Hornet Sportabout |  18.7 |     8 |  360   |  175 |   3.15 | 3.44  |  17.02 |    0 |    0 |      3 |      2 |
    | Valiant           |  18.1 |     6 |  225   |  105 |   2.76 | 3.46  |  20.22 |    1 |    0 |      3 |      1 |
    | Duster 360        |  14.3 |     8 |  360   |  245 |   3.21 | 3.57  |  15.84 |    0 |    0 |      3 |      4 |
    | Merc 240D         |  24.4 |     4 |  146.7 |   62 |   3.69 | 3.19  |  20    |    1 |    0 |      4 |      2 |
    | Merc 230          |  22.8 |     4 |  140.8 |   95 |   3.92 | 3.15  |  22.9  |    1 |    0 |      4 |      2 |
    | Merc 280          |  19.2 |     6 |  167.6 |  123 |   3.92 | 3.44  |  18.3  |    1 |    0 |      4 |      4 |

=== "Code"

    ```python title="docs/staging/tables.py" linenums="39"
    p.Raw(
        """
        Below an example of a regular markdown table. As it is very wide,
        horizontal scrolling is enabled by default. In addition, the number
        of rows is limited to 10 as there is no automatic paging available.
        """
    )
    p.add(md.Table(pd.DataFrame(mtcars).head(10), index=False))


    ```

---

## DataTable javascript library

=== "Content"

    Here the same table, but displayed using the 
    [DataTables](https://datatables.net/)  
    plugin. With this, we get automatic paging, searching as well as sorting
    by columns. 

    <table id='datatable_id-0' class='display' style='width:100%'> </table>

    ### Header filters

    Below a DataTable example with column filters in the header.
    The header in use is determined by the column type of the pandas
    table used for display. 

    - A numeric column gets a range selector
    - A categorical or boolean column a dropdown selection
    - Any other column a text-field.

    <table id='datatable_id-1' class='display' style='width:100%'> </table>

    ### Download buttons

    An example with buttons for downloading and printing
    of the table.

    <table id='datatable_id-2' class='display' style='width:100%'> </table>

=== "Code"

    ```python title="docs/staging/tables.py" linenums="49"
    p.Raw(
        """
        Here the same table, but displayed using the 
        [DataTables](https://datatables.net/)  
        plugin. With this, we get automatic paging, searching as well as sorting
        by columns. 
        """
    )
    # and as a DataTable
    p.DataTable(pd.DataFrame(mtcars))

    with p.H3("Header filters").ctx("nocode"):
        p.Raw(
            """
            Below a DataTable example with column filters in the header.
            The header in use is determined by the column type of the pandas
            table used for display. 

            - A numeric column gets a range selector
            - A categorical or boolean column a dropdown selection
            - Any other column a text-field.
            """
        )
        p.DataTable(ex_table, add_header_filters=True)

    with p.H3("Download buttons").ctx("nocode"):
        p.Raw(
            """
            An example with buttons for downloading and printing
            of the table.
            """
        )
        p.DataTable(ex_table, downloads=True)


    ```

---

<script>
$(document).ready( function () {
var myTable = $('#datatable_id-0').DataTable({"scrollX": "true", "columns": [{"title": "Name"}, {"title": "Mpg"}, {"title": "Cyl"}, {"title": "Disp"}, {"title": "Hp"}, {"title": "Drat"}, {"title": "Wt"}, {"title": "Qsec"}, {"title": "Vs"}, {"title": "Am"}, {"title": "Gear"}, {"title": "Carb"}], "ajax": "../tables_store/datatable-ca9b6f052f673e1d46f468ebb1ccc5d1.json"});

} );
</script>

[comment]: # (id: datatable_id-0)

<script>
$(document).ready( function () {
var myTable = $('#datatable_id-1').DataTable({"scrollX": "true", "columns": [{"title": "Name"}, {"title": "Age"}, {"title": "Hair"}, {"title": "Married"}], "ajax": "../tables_store/datatable-580c4149445c9b58b5740c532e20a5a0.json"});
yadcf.init(myTable, [{"column_number": 0, "filter_type": "text"}, {"column_number": 1, "filter_type": "range_number"}, {"column_number": 2, "filter_type": "select"}, {"column_number": 3, "filter_type": "select"}]);
} );
</script>

[comment]: # (id: datatable_id-1)

<script>
$(document).ready( function () {
var myTable = $('#datatable_id-2').DataTable({"scrollX": "true", "columns": [{"title": "Name"}, {"title": "Age"}, {"title": "Hair"}, {"title": "Married"}], "buttons": ["copy", "csv", "excel", "pdf", "print"], "dom": "<lfr>t<Bp>", "ajax": "../tables_store/datatable-580c4149445c9b58b5740c532e20a5a0.json"});

} );
</script>

[comment]: # (id: datatable_id-2)

## Tabulator javascript library

=== "Content"

    This time, we use the [Tabulator](http://tabulator.info)
    library. A library with a lot of interesting 
    functionality.

    <div id='tabulator_id-0' class='display'> </div>

    ### Header filters

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

    <div id='tabulator_id-1' class='display'> </div>

    ### Download buttons

    An example showing download buttons for export to csv, json or excel.

    <div id='tabulator_id-2' class='display'> </div><div>
      <button class="tabulator-btn-dwn", id="csv_down_id-0">to CSV</button>
      <button class="tabulator-btn-dwn", id="json_down_id-0">to JSON</button>
      <button class="tabulator-btn-dwn", id="xslx_down_id-0">to XLSX</button>
    </div>

=== "Code"

    ```python title="docs/staging/tables.py" linenums="84"
    p.Raw(
        """
        This time, we use the [Tabulator](http://tabulator.info)
        library. A library with a lot of interesting 
        functionality.
        """
    )
    p.Tabulator(
        pd.DataFrame(mtcars), add_header_filters=False, prettify_colnames=False
    )

    with p.H3("Header filters").ctx("nocode"):
        p.Raw(
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
        p.Tabulator(ex_table, add_header_filters=True, prettify_colnames=True)

    with p.H3("Download buttons").ctx("nocode"):
        p.P(
            """
            An example showing download buttons for export to csv, json or excel.
            """
        )
        p.Tabulator(
            ex_table,
            add_header_filters=True,
            prettify_colnames=True,
            downloads=True,
        )


    ```

---

<script>
var table = new Tabulator('#tabulator_id-0', {"layout": "fitDataTable", "pagination": true, "paginationSize": 10, "paginationSizeSelector": true, "columns": [{"field": "name", "title": "name"}, {"field": "mpg", "title": "mpg"}, {"field": "cyl", "title": "cyl"}, {"field": "disp", "title": "disp"}, {"field": "hp", "title": "hp"}, {"field": "drat", "title": "drat"}, {"field": "wt", "title": "wt"}, {"field": "qsec", "title": "qsec"}, {"field": "vs", "title": "vs"}, {"field": "am", "title": "am"}, {"field": "gear", "title": "gear"}, {"field": "carb", "title": "carb"}], "ajaxURL": "../tables_store/tabulator-c8469972d60cd61d98262704e068f4e9.json"});
</script>

[comment]: # (id: tabulator_id-0)

<script>
var table = new Tabulator('#tabulator_id-1', {"layout": "fitDataTable", "pagination": true, "paginationSize": 10, "paginationSizeSelector": true, "columns": [{"field": "name", "headerFilter": "input", "title": "Name"}, {"field": "age", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Age"}, {"field": "hair", "headerFilter": "select", "headerFilterParams": {"values": ["", "brown", "green", "red"]}, "title": "Hair"}, {"field": "married", "headerFilter": "tickCross", "formatter": "tickCross", "headerFilterParams": {"tristate": true}, "title": "Married"}], "ajaxURL": "../tables_store/tabulator-75b468c8a8bcf5fff9d211e88d0e6972.json"});
</script>

[comment]: # (id: tabulator_id-1)

<script>
var table = new Tabulator('#tabulator_id-2', {"layout": "fitDataTable", "pagination": true, "paginationSize": 10, "paginationSizeSelector": true, "columns": [{"field": "name", "headerFilter": "input", "title": "Name"}, {"field": "age", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Age"}, {"field": "hair", "headerFilter": "select", "headerFilterParams": {"values": ["", "brown", "green", "red"]}, "title": "Hair"}, {"field": "married", "headerFilter": "tickCross", "formatter": "tickCross", "headerFilterParams": {"tristate": true}, "title": "Married"}], "ajaxURL": "../tables_store/tabulator-75b468c8a8bcf5fff9d211e88d0e6972.json"});
//trigger download of data.csv file
$("#csv_down_id-0").click(function(){
    table.download("csv", "data.csv");
});

//trigger download of data.json file
$("#json_down_id-0").click(function(){
    table.download("json", "data.json");
});

//trigger download of data.xlsx file
$("#xslx_down_id-0").click(function(){
    table.download("xlsx", "data.xlsx", {sheetName:"data"});
});
</script>

[comment]: # (id: tabulator_id-2)
[comment]: # (id: csv_down_id-0)
[comment]: # (id: json_down_id-0)
[comment]: # (id: xslx_down_id-0)

## Notes

=== "Content"

    Internally, the tables are serialized to json so that 
    they can be displayed in the web-browser. For any types 
    that are non-native to json (e.g. Path-instances), as a
    default handler the `str` funtion is called. If this
    is not ok, please transform the table columns accordingly.

=== "Code"

    ```python title="docs/staging/tables.py" linenums="133"
    p.Raw(
        """
        Internally, the tables are serialized to json so that 
        they can be displayed in the web-browser. For any types 
        that are non-native to json (e.g. Path-instances), as a
        default handler the `str` funtion is called. If this
        is not ok, please transform the table columns accordingly.
        """
    )

    ```

---
