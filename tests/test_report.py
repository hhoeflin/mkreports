import pytest
from mkreports import Report


class TestPage:
    def test_page(self, tmp_path):
        report = Report.create(tmp_path / "test", report_name="Test")

        with pytest.raises(ValueError):
            report.page("testpage")

        # but this one should pass as we add the .md
        report.page("testpage.md")
