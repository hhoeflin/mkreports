from mkreports import md


def test_header():
    header_text = "This is a header"
    header1 = md.H1(header_text)
    header2 = md.H2(header_text)
    assert header1.process_all().format_text(" ", " ") == "\n# " + header_text + "\n\n"
    assert header2.process_all().format_text(" ", " ") == "\n## " + header_text + "\n\n"
