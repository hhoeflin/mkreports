---
css:
- https://cdn.datatables.net/1.11.3/css/jquery.dataTables.min.css
- https://unpkg.com/tabulator-tables@5.1.0/dist/css/tabulator.min.css
javascript:
- https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js
- https://cdn.datatables.net/1.11.3/js/jquery.dataTables.min.js
- https://unpkg.com/tabulator-tables@5.1.0/dist/js/tabulator.min.js
---


# Different ways of handling tables

Conveying information with tables is very important for 
any type of report. Standard tables in markdown format 
can be very useful for this for limited amout of data, but for 
larger tables more sophisticated libraries are needed. 

## Markdown tables

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

## DataTable javascript library

Here the same table, but displayed using the 
[DataTables](https://datatables.net/)  
plugin. With this, we get automatic paging, searching as well as sorting
by columns. 

<table id='datatable_id-0' class='display' style='width:100%'> </table>

<script>
$(document).ready( function () {
$('#datatable_id-0').DataTable({"scrollX": "true", "columns": [{"title": "name"}, {"title": "mpg"}, {"title": "cyl"}, {"title": "disp"}, {"title": "hp"}, {"title": "drat"}, {"title": "wt"}, {"title": "qsec"}, {"title": "vs"}, {"title": "am"}, {"title": "gear"}, {"title": "carb"}], "ajax": "../tables_gen_assets/datatable-ca9b6f052f673e1d46f468ebb1ccc5d1.json"});
} );
</script>

[comment]: # (id: datatable_id-0)

## Tabulator javascript library

This time, we use the [Tabulator](http://tabulator.info)
library. A library with a lot of interesting 
functionality. Currently limited support.

<div id='tabulator_id-0' class='display' style='width:100%'> </div>

<script>
var table = new Tabulator('#tabulator_id-0', {"autoColumns": true, "pagination": true, "paginationSize": 10, "paginationSizeSelector": true, "ajaxURL": "../tables_gen_assets/tabulator-c8469972d60cd61d98262704e068f4e9.json"});
</script>

[comment]: # (id: tabulator_id-0)

## Notes

Internally, the tables are serialized to json so that 
they can be displayed in the web-browser. For any types 
that are non-native to json (e.g. Path-instances), as a
default handler the `str` funtion is called. If this
is not ok, please transform the table columns accordingly.

