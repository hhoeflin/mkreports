from mkreports import md


def test_list():
    basic_text = (
        md.H1("First header") + md.H2("Second header") + md.P("This is a paragraph")
    )
    assert basic_text.process_all() == (
        "\n# First header\n\n## Second header\n\nThis is a paragraph\n\n"
    )
