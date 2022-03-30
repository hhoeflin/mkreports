from pathlib import Path

import pytest
from mkreports import NavEntry, Report


class TestPage:
    def test_page(self, tmp_path):
        report = Report.create(tmp_path / "test", report_name="Test")

        with pytest.raises(ValueError):
            report.page("testpage.foo")

        # but this one should pass as we add the .md
        report.page("testpage.md")
        # and the one without .md
        report.page("testpage2")

        # one with a more sophisticated navigation entry
        nav_entry = NavEntry(("Lvl1", "Lvl2"), Path("testpage3.md"))
        page = report.page(nav_entry)
        # check that a non-existing page gets None
        assert report.get_nav_entry(Path("foobar")) is None
        assert page.nav_entry == nav_entry
