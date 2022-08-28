import tempfile
from pathlib import Path
from typing import Any, List, NamedTuple

import pytest
from IPython.testing.globalipapp import get_ipython
from mkreports import Report, set_mkreports_dir


class InitIpShell(NamedTuple):
    ip: Any
    report: Report


@pytest.fixture(scope="module")
def ip_shell_init():
    # due to scope we need our own temporary directory
    with tempfile.TemporaryDirectory() as tmp_path:
        # set the paths that are used
        tmp_path = Path(tmp_path)
        report_dir = tmp_path / "test_report"
        set_mkreports_dir(report_dir)

        ip = get_ipython()
        assert ip is not None

        report = Report.create(report_dir, "Test report")

        ip.run_cell("%load_ext mkreports")
        ip.run_cell("%matplotlib inline")

        yield InitIpShell(ip=ip, report=report)


def files_console(report) -> List[Path]:
    return list(report.page("console/active.md").asset_path.glob("*"))


def test_pil(ip_shell_init):
    num_files_before = len(files_console(ip_shell_init.report))
    ip_shell_init.ip.run_cell(
        """
        import numpy as np
        from PIL import Image

        img_np = np.zeros((200, 400), dtype=np.uint8)
        img_np[:, 200:400] = 128
        img = Image.fromarray(img_np)
        img
        """
    )

    num_files_after = len(files_console(ip_shell_init.report))
    assert num_files_after - num_files_before == 1


def test_matplotlib(ip_shell_init):
    num_files_before = len(files_console(ip_shell_init.report))
    ip_shell_init.ip.run_cell(
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
        fig
        """
    )

    num_files_after = len(files_console(ip_shell_init.report))
    assert num_files_after - num_files_before == 1


def test_plotnine(ip_shell_init):
    num_files_before = len(files_console(ip_shell_init.report))
    ip_shell_init.ip.run_cell(
        """
        from plotnine import aes, facet_wrap, geom_point, ggplot, stat_smooth
        from plotnine.data import mtcars
        myplot = (
            ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
            + geom_point()
            + stat_smooth(method="lm")
            + facet_wrap("~gear")
        )
        myplot
        """
    )

    num_files_after = len(files_console(ip_shell_init.report))
    assert num_files_after - num_files_before == 1


def test_seaborn(ip_shell_init):
    num_files_before = len(files_console(ip_shell_init.report))
    ip_shell_init.ip.run_cell(
        """
        import seaborn as sns
        sns.set_theme(style="ticks")

        # Load the example dataset for Anscombe's quartet
        df = sns.load_dataset("anscombe")

        # Show the results of a linear regression within each dataset
        sea_fig = sns.lmplot(
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
        )
        sea_fig
        """
    )

    num_files_after = len(files_console(ip_shell_init.report))
    assert num_files_after - num_files_before == 1


def test_altair(ip_shell_init):
    num_files_before = len(files_console(ip_shell_init.report))
    ip_shell_init.ip.run_cell(
        """
        import altair as alt
        import pandas as pd

        source = pd.DataFrame(
            {
                "a": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
                "b": [28, 55, 43, 91, 81, 53, 19, 87, 52],
            }
        )

        alt_fig = alt.Chart(source).mark_bar().encode(x="a", y="b").properties(width=600)
        alt_fig
        """
    )

    num_files_after = len(files_console(ip_shell_init.report))
    assert num_files_after - num_files_before == 1


def test_plotly(ip_shell_init):
    num_files_before = len(files_console(ip_shell_init.report))
    ip_shell_init.ip.run_cell(
        """
        import plotly.express as px

        fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
        fig
        """
    )

    num_files_after = len(files_console(ip_shell_init.report))
    assert num_files_after - num_files_before == 1
