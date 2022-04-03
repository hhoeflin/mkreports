---
css:
- ../../javascript/assets/code_admonition.css
javascript:
- https://cdn.jsdelivr.net/npm/vega@5
- https://cdn.jsdelivr.net/npm/vega-lite@5
- https://cdn.jsdelivr.net/npm/vega-embed@6
- https://cdn.plot.ly/plotly-2.8.3.min.js
---


# Images

??? code "Code"

    ```python title="docs/staging/images.py"
    --8<-- 'docs/usage/images_store/images-904b9e74011d8731fcc104997285400a.py'
    ```

## Supported formats

Mkreports supports inclusion out of the box of a number of different imaging 
libraries. For each supported library, an example is show below.

For any not supported library, it is still possible to write out the 
image manually and then include it as an `ImageFile` object.

### PIL

=== "Content"

    PIL is the standard python image library. `Image` objects are written
    out to files and included in the markdown.

    Here as an example we simply have a black and white image of a black
    and grey square.
    ![](images_store/pil_image-c8343f974dc12426173f781a465749d2.png)

=== "Code"

    ```python title="docs/staging/images.py" linenums="33"
    p.Raw(
        """
        PIL is the standard python image library. `Image` objects are written
        out to files and included in the markdown.

        Here as an example we simply have a black and white image of a black
        and grey square.
        """
    )
    img_np = np.zeros((200, 400), dtype=np.uint8)
    img_np[:, 200:400] = 128
    img = Image.fromarray(img_np)
    p.PIL(img)


    ```

---

### Matplotlib

=== "Content"

    For many scientific graphing purposes, `matplotlib` is either the direct
    choice or the backend being used for plotting. 
    ![](images_store/image-9eacde53d07030438d059ea6a19b8285.png)

=== "Code"

    ```python title="docs/staging/images.py" linenums="49"
    p.Raw(
        """
        For many scientific graphing purposes, `matplotlib` is either the direct
        choice or the backend being used for plotting. 
        """
    )

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    p.Matplotlib(fig)


    ```

---

### Plotnine

=== "Content"

    Any plots created by `plotnine` can be included directly. The code below
    is from the beginner example of the library.
    ![](images_store/image-41a828f4fba906604a976d3f9ad1138a.png)

=== "Code"

    ```python title="docs/staging/images.py" linenums="61"
    p.Raw(
        """
        Any plots created by `plotnine` can be included directly. The code below
        is from the beginner example of the library.
        """
    )

    p.Plotnine(
        ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
        + geom_point()
        + stat_smooth(method="lm")
        + facet_wrap("~gear"),
    )


    ```

---

### Seaborn

=== "Content"

    Another well known option is Seaborn. The interface is similar to the 
    ones before. Under the hood, the `figure` attribute of the seaborn plot is 
    accessed and saved in the same fashion as for matplotlib.
    ![](images_store/image-c3fb8cb2918f73795ffbae41eb5404ae.png)

=== "Code"

    ```python title="docs/staging/images.py" linenums="76"
    p.add(
        """
        Another well known option is Seaborn. The interface is similar to the 
        ones before. Under the hood, the `figure` attribute of the seaborn plot is 
        accessed and saved in the same fashion as for matplotlib.
        """
    )

    sns.set_theme(style="ticks")

    # Load the example dataset for Anscombe's quartet
    df = sns.load_dataset("anscombe")

    # Show the results of a linear regression within each dataset
    p.Seaborn(
        sns.lmplot(
            x="x",
            y="y",
            col="dataset",
            hue="dataset",
            data=df,
            col_wrap=2,
            ci=None,
            palette="muted",
            height=4,
            scatter_kws={"s": 50, "alpha": 1},
        ),
    )


    ```

---

### Altair

=== "Content"

    <div id='altair_id-0'> </div>

=== "Code"

    ```python title="docs/staging/images.py" linenums="106"
    import altair as alt
    import pandas as pd

    source = pd.DataFrame(
        {
            "a": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
            "b": [28, 55, 43, 91, 81, 53, 19, 87, 52],
        }
    )

    p.Altair(
        alt.Chart(source).mark_bar().encode(x="a", y="b").properties(width=600)
    )


    ```

---

<script>
    vegaEmbed("#altair_id-0", "../images_store/altair-a7a2eb773c7d9454c694b490a77e5a7e.csv")
    // result.view provides access to the Vega View API
    .then(result => console.log(result))
    .catch(console.warn);
</script>

[comment]: # (id: altair_id-0)

### Plotly

=== "Content"

    <div id='plotly_id-0'> </div>

=== "Code"

    ```python title="docs/staging/images.py" linenums="121"
    import plotly.express as px

    fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    p.Plotly(fig)


    ```

---

<script>
    fetch('../images_store/plotly-2c4e085bcb294e03c4c01a147570a8c5.json')
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            doPlotly(data);
        })
        .catch(function (err) {
            console.log('error: ' + err);
        });
    function doPlotly(plotlyJson) {
        Plotly.newPlot("plotly_id-0", {
            "data": plotlyJson["data"],
            "layout": plotlyJson["layout"]
        })
    }
</script>

[comment]: # (id: plotly_id-0)

## Different image sizes

In order to change the size of the image, use the width
and height parameters. But please note that ultimately,
the number of pixels determines the size  - i.e. doubling height
and width while halfing dpi does not change the size, but 
internally how it is rendered may change.

### Plotnine

=== "Content"

    #### Larger

    ![](images_store/image-3ec0200f5d28f661895e19b17605e80f.png)

    #### Smaller

    ![](images_store/image-938d1d3f8e637526be808c610415dfb9.png)

=== "Code"

    ```python title="docs/staging/images.py" linenums="139"
    p.H4("Larger")
    p.Plotnine(
        ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
        + geom_point()
        + stat_smooth(method="lm")
        + facet_wrap("~gear"),
        width=10,
        height=6,
    )
    p.H4("Smaller")
    p.Plotnine(
        ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
        + geom_point()
        + stat_smooth(method="lm")
        + facet_wrap("~gear"),
        width=5,
        height=3,
    )


    ```

---

## Images next to each other

Images can also be placed next to each other, if there is enough
space. Just specify them directly one after the other and if there
is enough space, they will be placed next to each other.

![](images_store/image-a35a8295fcfec10230f14551e39d8969.png)
![](images_store/image-a35a8295fcfec10230f14551e39d8969.png)
