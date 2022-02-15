from mkreports.code_context import CodeContext
from mkreports.md import Code, MdSeq, Raw, Tab


def test_code_context():
    with CodeContext(layout="tabbed", add_bottom=True, stack_level=1) as con:
        pass
        con.add(Raw("Test"))

    con_md = con.md_obj()
    assert isinstance(con_md, MdSeq)
    items = con_md.items
    assert isinstance(items[0], Tab)
    assert isinstance(items[1], Tab)
    assert isinstance(items[0].text, MdSeq)
    assert len(items[0].text) == 1
    assert isinstance(items[0].text[0], Raw)
    assert isinstance(items[1].text, Code)
