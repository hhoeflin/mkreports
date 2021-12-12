from pathlib import Path

import pytest
from mkreports import settings


def test_settings():
    # merge two requirements
    req1 = settings.Settings(mkdocs=dict(top=["test"]))
    req2 = settings.Settings(mkdocs=dict(top=["test2"]))
    req_nav = settings.Settings(mkdocs=dict(nav=["test2"]))

    assert req1 + req2 == settings.Settings(mkdocs=dict(top=["test", "test2"]))
    assert req1 + req2 != req1
    assert req1 + req1 == req1

    # make sure an error occurs if nav is merged
    # but nav in one of both is allowed
    assert req1 + req_nav == settings.Settings(mkdocs=dict(nav=["test2"], top=["test"]))
    with pytest.raises(ValueError):
        req_nav + req_nav


def test_path_nav_entry():
    """
    Test the way to and from the nav entry as well as the merging
    """
    test_page = Path("test/test2/test3.md")
    test_page2 = Path("test/test4/test5.md")
    base_nav = (["Home"], Path("index.md"))

    test_nav = settings.path_to_nav_entry(test_page)
    test_nav2 = settings.path_to_nav_entry(test_page2)
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
    nav_list = settings.mkdocs_to_nav(mkdocs_nav)
    assert nav_list == [base_nav, test_nav, test_nav2]
    assert mkdocs_nav == settings.nav_to_mkdocs(nav_list)
