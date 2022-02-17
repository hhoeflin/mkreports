---
css:
- https://unpkg.com/tabulator-tables@5.1.0/dist/css/tabulator.min.css
javascript:
- https://unpkg.com/tabulator-tables@5.1.0/dist/js/tabulator.min.js
- ../javascript/min_max_filter.js
---


# Quickstart

First, below the code that was used to create this page. 
It is a very brief example of an page with a table and an image
as well as some text, like here.

```python
--8<-- 'docs/quickstart_store/quickstart-e782f294b2819da0bca02b03259b347e.py'
```

We are quickly analyzing the mtcars dataset 
that is included with plotnine.

## Data as a table

=== "Content"

    <div id='tabulator_id-0' class='display'> </div>

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="31"
    p.Tabulator(mtcars, add_header_filters=True, prettify_colnames=True)


    ```

---

<script>
var table = new Tabulator('#tabulator_id-0', {"layout": "fitDataTable", "pagination": true, "paginationSize": 10, "paginationSizeSelector": true, "columns": [{"field": "name", "headerFilter": "input", "title": "Name"}, {"field": "mpg", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Mpg"}, {"field": "cyl", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Cyl"}, {"field": "disp", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Disp"}, {"field": "hp", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Hp"}, {"field": "drat", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Drat"}, {"field": "wt", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Wt"}, {"field": "qsec", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Qsec"}, {"field": "vs", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Vs"}, {"field": "am", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Am"}, {"field": "gear", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Gear"}, {"field": "carb", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Carb"}], "ajaxURL": "../quickstart_store/tabulator-c8469972d60cd61d98262704e068f4e9.json"});
</script>

[comment]: # (id: tabulator_id-0)

## Some simple plots

=== "Content"

    ![](quickstart_store/image-41a828f4fba906604a976d3f9ad1138a.png)

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="35"
    p.Image(
        (
            p9.ggplot(mtcars, p9.aes("wt", "mpg", color="factor(gear)"))
            + p9.geom_point()
            + p9.stat_smooth(method="lm")
            + p9.facet_wrap("~gear")
        )
    )


    ```

---

# Quickstart

First, below the code that was used to create this page. 
It is a very brief example of an page with a table and an image
as well as some text, like here.

```python
--8<-- 'docs/quickstart_store/quickstart-af9d815edefb91666aeb23523ce87630.py'
```

We are quickly analyzing the mtcars dataset 
that is included with plotnine.

## Data as a table

# Quickstart

First, below the code that was used to create this page. 
It is a very brief example of an page with a table and an image
as well as some text, like here.

```python
--8<-- 'docs/quickstart_store/quickstart-af9d815edefb91666aeb23523ce87630.py'
```

We are quickly analyzing the mtcars dataset 
that is included with plotnine.

## Data as a table

=== "Content"

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="30"
    p.Tabulator(mtcars, add_header_filters=True, prettify_colnames=True)


    ```

---

# Quickstart

First, below the code that was used to create this page. 
It is a very brief example of an page with a table and an image
as well as some text, like here.

```python
--8<-- 'docs/quickstart_store/quickstart-af9d815edefb91666aeb23523ce87630.py'
```

We are quickly analyzing the mtcars dataset 
that is included with plotnine.

## Data as a table

=== "Content"

    <div id='tabulator_id-1' class='display'> </div>

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="30"
    p.Tabulator(mtcars, add_header_filters=True, prettify_colnames=True)


    ```

---

<script>
var table = new Tabulator('#tabulator_id-1', {"layout": "fitDataTable", "pagination": true, "paginationSize": 10, "paginationSizeSelector": true, "columns": [{"field": "name", "headerFilter": "input", "title": "Name"}, {"field": "mpg", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Mpg"}, {"field": "cyl", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Cyl"}, {"field": "disp", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Disp"}, {"field": "hp", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Hp"}, {"field": "drat", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Drat"}, {"field": "wt", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Wt"}, {"field": "qsec", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Qsec"}, {"field": "vs", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Vs"}, {"field": "am", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Am"}, {"field": "gear", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Gear"}, {"field": "carb", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Carb"}], "ajaxURL": "../quickstart_store/tabulator-c8469972d60cd61d98262704e068f4e9.json"});
</script>

[comment]: # (id: tabulator_id-1)

## Some simple plots

=== "Content"

    ![](quickstart_store/image-41a828f4fba906604a976d3f9ad1138a.png)

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="34"
    p.Image(
        (
            p9.ggplot(mtcars, p9.aes("wt", "mpg", color="factor(gear)"))
            + p9.geom_point()
            + p9.stat_smooth(method="lm")
            + p9.facet_wrap("~gear")
        )
    )


    ```

---

# Quickstart

First, below the code that was used to create this page. 
It is a very brief example of an page with a table and an image
as well as some text, like here.

```python
--8<-- 'docs/quickstart_store/quickstart-af9d815edefb91666aeb23523ce87630.py'
```

We are quickly analyzing the mtcars dataset 
that is included with plotnine.

## Data as a table

=== "Content"

    <div id='tabulator_id-2' class='display'> </div>

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="30"
    p.Tabulator(mtcars, add_header_filters=True, prettify_colnames=True)


    ```

---

<script>
var table = new Tabulator('#tabulator_id-2', {"layout": "fitDataTable", "pagination": true, "paginationSize": 10, "paginationSizeSelector": true, "columns": [{"field": "name", "headerFilter": "input", "title": "Name"}, {"field": "mpg", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Mpg"}, {"field": "cyl", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Cyl"}, {"field": "disp", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Disp"}, {"field": "hp", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Hp"}, {"field": "drat", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Drat"}, {"field": "wt", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Wt"}, {"field": "qsec", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Qsec"}, {"field": "vs", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Vs"}, {"field": "am", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Am"}, {"field": "gear", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Gear"}, {"field": "carb", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Carb"}], "ajaxURL": "../quickstart_store/tabulator-c8469972d60cd61d98262704e068f4e9.json"});
</script>

[comment]: # (id: tabulator_id-2)

## Some simple plots

=== "Content"

    ![](quickstart_store/image-41a828f4fba906604a976d3f9ad1138a.png)

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="34"
    p.Image(
        (
            p9.ggplot(mtcars, p9.aes("wt", "mpg", color="factor(gear)"))
            + p9.geom_point()
            + p9.stat_smooth(method="lm")
            + p9.facet_wrap("~gear")
        )
    )


    ```

---

# Quickstart

First, below the code that was used to create this page. 
It is a very brief example of an page with a table and an image
as well as some text, like here.

```python
--8<-- 'docs/quickstart_store/quickstart-af9d815edefb91666aeb23523ce87630.py'
```

We are quickly analyzing the mtcars dataset 
that is included with plotnine.

## Data as a table

=== "Content"

    <div id='tabulator_id-3' class='display'> </div>

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="30"
    p.Tabulator(mtcars, add_header_filters=True, prettify_colnames=True)


    ```

---

<script>
var table = new Tabulator('#tabulator_id-3', {"layout": "fitDataTable", "pagination": true, "paginationSize": 10, "paginationSizeSelector": true, "columns": [{"field": "name", "headerFilter": "input", "title": "Name"}, {"field": "mpg", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Mpg"}, {"field": "cyl", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Cyl"}, {"field": "disp", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Disp"}, {"field": "hp", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Hp"}, {"field": "drat", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Drat"}, {"field": "wt", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Wt"}, {"field": "qsec", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Qsec"}, {"field": "vs", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Vs"}, {"field": "am", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Am"}, {"field": "gear", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Gear"}, {"field": "carb", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Carb"}], "ajaxURL": "../quickstart_store/tabulator-c8469972d60cd61d98262704e068f4e9.json"});
</script>

[comment]: # (id: tabulator_id-3)

## Some simple plots

=== "Content"

    ![](quickstart_store/image-41a828f4fba906604a976d3f9ad1138a.png)

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="34"
    p.Image(
        (
            p9.ggplot(mtcars, p9.aes("wt", "mpg", color="factor(gear)"))
            + p9.geom_point()
            + p9.stat_smooth(method="lm")
            + p9.facet_wrap("~gear")
        )
    )


    ```

---

# Quickstart

First, below the code that was used to create this page. 
It is a very brief example of an page with a table and an image
as well as some text, like here.

```python
--8<-- 'docs/quickstart_store/quickstart-af9d815edefb91666aeb23523ce87630.py'
```

We are quickly analyzing the mtcars dataset 
that is included with plotnine.

## Data as a table

=== "Content"

    <div id='tabulator_id-4' class='display'> </div>

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="30"
    p.Tabulator(mtcars, add_header_filters=True, prettify_colnames=True)


    ```

---

<script>
var table = new Tabulator('#tabulator_id-4', {"layout": "fitDataTable", "pagination": true, "paginationSize": 10, "paginationSizeSelector": true, "columns": [{"field": "name", "headerFilter": "input", "title": "Name"}, {"field": "mpg", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Mpg"}, {"field": "cyl", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Cyl"}, {"field": "disp", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Disp"}, {"field": "hp", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Hp"}, {"field": "drat", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Drat"}, {"field": "wt", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Wt"}, {"field": "qsec", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Qsec"}, {"field": "vs", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Vs"}, {"field": "am", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Am"}, {"field": "gear", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Gear"}, {"field": "carb", "width": 80, "headerFilter": minMaxFilterEditor, "headerFilterFunc": minMaxFilterFunction, "headerFilterLiveFilter": false, "title": "Carb"}], "ajaxURL": "../quickstart_store/tabulator-c8469972d60cd61d98262704e068f4e9.json"});
</script>

[comment]: # (id: tabulator_id-4)

## Some simple plots

=== "Content"

    ![](quickstart_store/image-41a828f4fba906604a976d3f9ad1138a.png)

=== "Code"

    ```python title="docs/staging/quickstart.py" linenums="34"
    p.Image(
        (
            p9.ggplot(mtcars, p9.aes("wt", "mpg", color="factor(gear)"))
            + p9.geom_point()
            + p9.stat_smooth(method="lm")
            + p9.facet_wrap("~gear")
        )
    )


    ```

---
