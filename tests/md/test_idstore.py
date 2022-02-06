from mkreports.md import IDStore


def test_idstore():
    idstore = IDStore(start_with=1, used_ids=set(["foo-1", "bar-2", "baz_1"]))

    assert idstore.next_id("foo") == "foo-2"  # foo-1 already used
    assert idstore.next_id("bar") == "bar-1"
    assert idstore.next_id("bar") == "bar-3"  # bar-2 already used
    assert idstore.next_id("baz") == "baz-1"  # baz_1 is not a correct id

    assert idstore._used == set(
        ["foo-1", "foo-2", "bar-1", "bar-2", "bar-3", "baz_1", "baz-1"]
    )
