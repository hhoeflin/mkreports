from mkreports import md


def test_raw():
    test_string = "This is a string"
    raw = md.Raw(test_string)
    assert str(raw.to_markdown().body) == test_string


def test_paragraph():
    test_paragraph = "This is a paragraph"
    p = md.P(test_paragraph)
    assert (
        p.to_markdown().body.format_text(" ", " ") == "\n\n" + test_paragraph + "\n\n"
    )


def test_mdseq():
    """Test that sequences of MdObj work."""
    # check that an empty MdSeq object does not throw an error
    md_seq = md.MdSeq(())
    assert md_seq.to_markdown() == md.MdOut()
