from mkreports import md


def test_raw():
    test_string = "This is a string"
    raw = md.Raw(test_string)
    assert str(raw.to_markdown()) == test_string


def test_paragraph():
    test_paragraph = "This is a paragraph"
    p = md.P(test_paragraph)
    assert p.to_markdown().format_text(" ", " ") == "\n" + test_paragraph + "\n\n"
