import pytest
from mkreports import Report, md


class TestPage:
    def test_page(self, tmp_path):
        report = Report(tmp_path / "test", site_name="Test")

        with pytest.raises(ValueError):
            report.page("testpage")

        # but this one should pass as we add the .md
        report.page("testpage.md")
