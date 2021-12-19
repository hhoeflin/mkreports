from pathlib import Path

from mkreports import Report, md


class TestPage:
    def test_ctx(self, tmp_path):
        report = Report(tmp_path / "test", site_name="Test")

        initial_store_path = tmp_path / "initial_path"
        md.set_default_store_path(initial_store_path)

        with report.get_page("testpage.md") as p:
            assert md.get_default_store_path() == p.gen_asset_path

        assert md.get_default_store_path() == initial_store_path
