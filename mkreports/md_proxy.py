import inspect
from functools import partial

from . import md


class MdProxy:
    def __init__(self, store_path):
        self.store_path = store_path

    def __getattr__(self, name):
        # we are not checking if it is included; if not, should raise error
        obj = getattr(md, name)

        # if is a class; try to fix the init method
        if inspect.isclass(obj):
            # check the init method signature
            obj_sig = inspect.signature(obj)
            if "store_path" in obj_sig.parameters:
                return partial(obj, store_path=self.store_path)
            else:
                return obj

        else:
            return obj
