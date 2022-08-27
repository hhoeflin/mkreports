from mkreports import md


def test_raw():
    test_string = "This is a string"
    raw = md.Raw(test_string)
    assert str(raw.render().body) == test_string


def test_paragraph():
    test_paragraph = "This is a paragraph"
    p = md.P(test_paragraph)
    assert p.render().body.format_text(" ", " ") == "\n\n" + test_paragraph + "\n\n"


def test_mdseq_empty():
    """Test that sequences of MdObj work."""
    # check that an empty MdSeq object does not throw an error
    md_seq = md.MdSeq(())
    assert md_seq.render().body == md.SpacedText("")
    assert md_seq.render().back == md.SpacedText("")


def test_md_seq_full():
    basic_md_seq = (
        md.H1("First header") + md.H2("Second header") + md.P("This is a paragraph")
    )
    assert basic_md_seq.render_fixtures() == set()
    rendered = basic_md_seq.render()
    assert rendered.body.format_text(" ", "a") == (
        "\n\n# First header\n\n## Second header\n\nThis is a paragraph\n\n"
    )
