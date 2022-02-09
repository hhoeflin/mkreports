import inspect
from functools import partial
from pathlib import Path
from typing import Any, Dict

from . import md


def register_md(name):
    def register_md_named(cls):
        MdProxy.proxied_classes[name] = cls
        return cls

    return register_md_named


class MdProxy:
    proxied_classes: Dict[str, Any] = dict()

    def __init__(self, store_path: Path, report_path: Path, javascript_path: Path):
        self.store_path = store_path
        self.report_path = report_path
        self.javascript_path = javascript_path

    def __getattr__(self, name):
        # we are not checking if it is included; if not, should raise error
        if name in self.proxied_classes:
            obj = self.proxied_classes[name]
        else:
            raise AttributeError(name)

        # if is a class; try to fix the init method
        if inspect.isclass(obj):
            # check the init method signature
            partial_kwargs = {}
            obj_sig = inspect.signature(obj)
            if "store_path" in obj_sig.parameters:
                partial_kwargs["store_path"] = self.store_path
            if "report_path" in obj_sig.parameters:
                partial_kwargs["report_path"] = self.report_path
            if "javascript_path" in obj_sig.parameters:
                partial_kwargs["javascript_path"] = self.javascript_path

            if len(partial_kwargs) > 0:
                return partial(obj, **partial_kwargs)
            else:
                return obj

        else:
            return obj
