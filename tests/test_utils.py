from pathlib import Path

from mkreports import utils


def test_path_nav_entry():
    """
    Test the way to and from the nav entry as well as the merging
    """
    test_page = Path("test/test2/test3.md")
    test_page2 = Path("test/test4/test5.md")
    base_nav = (["Home"], Path("index.md"))

    test_nav = utils.path_to_nav_entry(test_page)
    test_nav2 = utils.path_to_nav_entry(test_page2)
    assert test_nav == (["Test", "Test2", "Test3"], test_page)

    mkdocs_nav = [
        {"Home": "index.md"},
        {
            "Test": [
                {"Test2": [{"Test3": str(test_page)}]},
                {"Test4": [{"Test5": str(test_page2)}]},
            ]
        },
    ]

    # make a round trip
    nav_list = utils.mkdocs_to_nav(mkdocs_nav)
    assert nav_list == [base_nav, test_nav, test_nav2]
    assert mkdocs_nav == utils.nav_to_mkdocs(nav_list)
