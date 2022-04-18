from pathlib import Path

import pytest
from mkreports.md import Settings as MdSettings
from mkreports.settings import (NavEntry, mkdocs_to_navlist, navlist_to_mkdocs,
                                path_to_nav_entry)


def test_settings():
    # merge two requirements
    req1 = MdSettings(mkdocs=dict(top=["test"]))
    req2 = MdSettings(mkdocs=dict(top=["test2"]))
    req_nav = MdSettings(mkdocs=dict(nav=["test2"]))

    assert req1 + req2 == MdSettings(mkdocs=dict(top=["test", "test2"]))
    assert req1 + req2 != req1
    assert req1 + req1 == req1

    # make sure an error occurs if nav is merged
    # but nav in one of both is allowed
    assert req1 + req_nav == MdSettings(mkdocs=dict(nav=["test2"], top=["test"]))
    with pytest.raises(ValueError):
        req_nav + req_nav


def test_path_nav_entry():
    """
    Test the way to and from the nav entry as well as the merging
    """
    test_page = Path("test/test2/test3.md")
    test_page2 = Path("test/test4/test5.md")
    base_nav = (["Home"], Path("index.md"))

    test_nav = path_to_nav_entry(test_page)
    test_nav2 = path_to_nav_entry(test_page2)
    assert test_nav == NavEntry(tuple(["Test", "Test2", "Test3"]), test_page)

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
    nav_list = mkdocs_to_navlist(mkdocs_nav)
    assert nav_list == [base_nav, test_nav, test_nav2]
    assert mkdocs_nav == navlist_to_mkdocs(nav_list)
