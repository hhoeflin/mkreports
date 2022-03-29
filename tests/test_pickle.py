import pickle
from pathlib import Path
from typing import Any

from mkreports import Report


def pickle_roundtrip(obj: Any, file: Path):
    """
    Pickle an item into a temporary file and then reload and compare.
    """
    with file.open("wb") as f:
        pickle.dump(obj, f)
    with file.open("rb") as f:
        obj_reload = pickle.load(f)

    assert obj == obj_reload


def test_pickle(tmp_path):
    report = Report.create(tmp_path, report_name="test report")
    page = report.page("test_page")

    pickle_roundtrip(page._md.page_info.idstore, tmp_path / "idstore.pkl")
    pickle_roundtrip(page._md, tmp_path / "md.pkl")
    pickle_roundtrip(page, tmp_path / "page.pkl")
    pickle_roundtrip(report, tmp_path / "report.pkl")
