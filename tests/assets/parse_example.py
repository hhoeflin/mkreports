from pathlib import Path

import mkreports
import pytest


# define some functions
def A():
    a = 0
    b = 1
    for i in range(10):
        a += i
        b *= i
    return (a, b)


def B():
    return A()
