from mkreports import md


def test_raw():
    test_string = "This is a string"
    raw = md.Raw(test_string)
    assert str(raw.body) == test_string


def test_paragraph():
    test_paragraph = "This is a paragraph"
    p = md.P(test_paragraph)
    assert p.body.format_text(" ", " ") == "\n\n" + test_paragraph + "\n\n"


def test_mdseq():
    """Test that sequences of MdObj work."""
    # check that an empty MdSeq object does not throw an error
    md_seq = md.MdSeq(())
    assert md_seq.body == md.SpacedText("")
    assert md_seq.back == md.SpacedText("")
