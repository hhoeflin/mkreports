from mkreports import md


def test_spaced_text():
    """
    A number of tests to ensure that spaced text works.
    """

    a = md.SpacedText(a_str := "\nText 1\n\n", (3, 2))
    b = md.SpacedText(b_str := "\nText 2\nand something\nand else\n", (4, 2))

    assert a + "test" == md.SpacedText(a_str + "test", (3, 0))
    assert "test" + a == md.SpacedText("test" + "\n\n" + a_str, (0, 2))
    assert a + b == md.SpacedText(a_str + "\n" + b_str, (3, 2))
