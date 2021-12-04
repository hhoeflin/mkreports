from mkreports import md


def test_raw():
    test_string = "This is a string"
    raw = md.Raw(test_string)
    assert str(raw.process_all()) == test_string


def test_paragraph():
    test_paragraph = "This is a paragraph"
    p = md.P(test_paragraph)
    assert p.process_all().format_text(" ", " ") == "\n" + test_paragraph + "\n\n"
