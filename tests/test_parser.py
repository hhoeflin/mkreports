from pathlib import Path

import pytest
from mkreports.parser import (closest_after, closest_before, get_stmt_ranges,
                              smallest_overlap)

pyfile = Path(__file__).parent / "assets" / "parse_example.py"


@pytest.fixture
def stmt_tree():
    return get_stmt_ranges(pyfile)


def test_get_stmt_ranges(stmt_tree):
    assert len(stmt_tree) == 12


def test_closest_before(stmt_tree):
    before_in_for = closest_before(stmt_tree, 12)
    assert before_in_for is not None
    assert (before_in_for.begin, before_in_for.end) == (11, 14)

    before_b_1 = closest_before(stmt_tree, 10)
    assert before_b_1 is not None
    assert (before_b_1.begin, before_b_1.end) == (9, 10)

    before_pathlib = closest_before(stmt_tree, 1)
    assert before_pathlib is None


def test_closest_after(stmt_tree):
    after_in_for = closest_after(stmt_tree, 13)
    assert after_in_for is not None
    assert (after_in_for.begin, after_in_for.end) == (14, 15)

    after_b_1 = closest_after(stmt_tree, 10)
    assert after_b_1 is not None
    assert (after_b_1.begin, after_b_1.end) == (11, 14)

    after_last_return = closest_after(stmt_tree, 18)
    assert after_last_return is None


def test_smallest_overlap(stmt_tree):
    assert smallest_overlap(stmt_tree, 15) is None
    in_for = smallest_overlap(stmt_tree, 11)
    assert in_for is not None
    assert (in_for.begin, in_for.end) == (11, 14)
