"""
A simple class to provide access to full extent
of statements with starting and ending lines.
"""
import ast
from pathlib import Path
from typing import Optional, Tuple

from intervaltree import Interval, IntervalTree


def get_stmt_ranges(pyfile: Path) -> IntervalTree:
    """
    Parse the python file and return the ranges of all statements.

    Here, we only return the range of the statements at the lowest level.
    This is to make it easier to find the 'previous' statement.
    The line numbers in the interval tree will be 1-based.
    """
    # first we parse the python file into an AST
    with pyfile.open("r") as f:
        file_ast = ast.parse(f.read())
    inttree = IntervalTree()

    # now we want to walk along the tree and get the line extent of
    # all nodes that are statements; as data payload we attach
    # the parsed nodes
    for node in ast.walk(file_ast):
        if isinstance(node, ast.stmt):
            if node.lineno is not None and node.end_lineno is not None:
                inttree.add(
                    Interval(begin=node.lineno, end=node.end_lineno + 1, data=node)
                )

    return inttree


def smallest_overlap(tree: IntervalTree, lineno: int) -> Optional[Interval]:
    """
    Find the closest match that overlaps and is shortests.
    """
    overlap_set = tree.at(lineno)
    if len(overlap_set) > 0:
        # we take the shortest
        overlap_list = list(overlap_set)
        overlap_list.sort(key=lambda x: x.end - x.begin)
        return overlap_list[0]
    else:
        return None


def closest_before(tree: IntervalTree, lineno: int) -> Optional[Interval]:
    """
    Return the closest item strictly before lineno.
    """
    tree_list = list(tree.items())
    # sort by size of element; this will be retained in later sorts
    tree_list.sort(key=lambda x: x.end - x.begin)
    # here we filter by those that come before and
    # sort by the difference to the current line
    before_list = [x for x in tree_list if (x.begin < lineno)]
    before_list.sort(key=lambda x: lineno - x.begin)
    if len(before_list) > 0:
        return before_list[0]
    else:
        return None


def closest_after(tree: IntervalTree, lineno: int) -> Optional[Interval]:
    """
    Return the closest item strictly before lineno.
    """
    tree_list = list(tree.items())
    # sort by size of element; this will be retained in later sorts
    tree_list.sort(key=lambda x: x.end - x.begin)
    # here we filter by those that come before and
    # sort by the difference to the current line
    # rest by difference to current line
    after_list = [x for x in tree_list if (x.begin > lineno)]
    after_list.sort(key=lambda x: x.begin - lineno)
    if len(after_list) > 0:
        return after_list[0]
    else:
        return None


def envelope(tree: IntervalTree, pos: Interval) -> Optional[Interval]:
    tree_list = list(tree.envelope(pos.begin - 1, pos.end))
    if len(tree_list) == 0:
        return None
    else:
        tree_list.sort(key=lambda x: x.end - x.begin)
        return tree_list[0]


def get_neighbors(
    tree: IntervalTree, lineno: int
) -> Tuple[Optional[Interval], Optional[Interval], Optional[Interval]]:
    """
    For a given lineno, get the current statement (if there is one), as well
    as the previous and next statements in the tree.
    """
    return (
        closest_before(tree, lineno),
        smallest_overlap(tree, lineno),
        closest_after(tree, lineno),
    )
