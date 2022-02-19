import inspect
from functools import partial, update_wrapper
from typing import Any, Dict

from .settings import PageInfo


def register_md(name):
    def register_md_named(cls):
        MdProxy._proxied_classes[name] = cls
        return cls

    return register_md_named


class MdProxy:
    _proxied_classes: Dict[str, Any] = dict()

    def __init__(self, page_info: PageInfo):
        self.page_info = page_info

    def __getattr__(self, name):
        # we are not checking if it is included; if not, should raise error
        if name in self._proxied_classes:
            obj = self._proxied_classes[name]
        else:
            raise AttributeError(f"No MdObj of name '{name}' registered")

        # if is a class; try to fix the init method
        if inspect.isclass(obj):
            # check the init method signature
            partial_kwargs = {}
            obj_sig = inspect.signature(obj)
            if "page_info" in obj_sig.parameters:
                partial_kwargs["page_info"] = self.page_info

            if len(partial_kwargs) > 0:
                partial_obj = partial(obj, **partial_kwargs)
                update_wrapper(partial_obj, obj)
                partial_obj.__doc__ = obj.__init__.__doc__
                return partial_obj
            else:
                return obj

        else:
            return obj

    @property
    def proxied_clases(self):
        return self._proxied_classes
