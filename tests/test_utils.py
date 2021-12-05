from pathlib import Path

from mkreports import utils


def test_path_nav_entry():
    """
    Test the way to and from the nav entry as well as the merging
    """
    test_page = "test/test2/test3.md"
    base_nav = [{"Home": "index.md"}]

    test_nav = utils.path_to_nav_entry(Path(test_page))
    assert test_nav == [{"Test": [{"Test2": [{"Test3": test_page}]}]}]
    assert Path(test_page) == utils.path_from_nav_entry(test_nav)

    # and now also test the merging
    assert utils.nav_merger.merge(base_nav, test_nav) == [
        {"Home": "index.md"},
        {"Test": [{"Test2": [{"Test3": test_page}]}]},
    ]
