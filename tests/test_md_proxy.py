from functools import partial

from mkreports.md import MdProxy


def test_md_proxy(page_info):
    md_proxy = MdProxy(page_info=page_info, md_defaults=dict(Table=dict(max_rows=1000)))
    test_table = md_proxy.Table

    assert isinstance(test_table, partial)
    assert test_table.keywords["max_rows"] == 1000
