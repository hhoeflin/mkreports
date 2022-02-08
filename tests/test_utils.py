from mkreports import Report
from mkreports.utils import find_comment_ids
from plotnine.data import mtcars


def test_find_comment_ids(tmp_path):
    """Test if comment ids are appropriately parsed."""
    # we create a new report, write out several
    # datatables and check that the ids are correctly
    # discovered.
    report = Report.create(tmp_path, report_name="Comment Ids test")
    page = report.page("test")

    # two datatable and tabulator ids should show up
    page.DataTable(mtcars)
    page.DataTable(mtcars)
    page.Tabulator(mtcars)
    page.Tabulator(mtcars)

    # read the page
    with page.path.open("r") as f:
        page_text = f.read()

    comment_ids = find_comment_ids(page_text)

    assert comment_ids == set(
        [
            "datatable_id-0",
            "datatable_id-1",
            "tabulator_id-0",
            "tabulator_id-1",
        ]
    )
