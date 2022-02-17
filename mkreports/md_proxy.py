import inspect
from functools import partial
from pathlib import Path
from typing import Any, Dict

from .md.idstore import IDStore


def register_md(name):
    def register_md_named(cls):
        MdProxy._proxied_classes[name] = cls
        return cls

    return register_md_named


class MdProxy:
    _proxied_classes: Dict[str, Any] = dict()

    def __init__(
        self,
        store_path: Path,
        report_path: Path,
        page_path: Path,
        idstore: IDStore,
        javascript_path: Path,
        project_root: Path,
    ):
        self.store_path = store_path
        self.report_path = report_path
        self.javascript_path = javascript_path
        self.project_root = project_root
        self.page_path = page_path
        self.idstore = idstore

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
            if "store_path" in obj_sig.parameters:
                partial_kwargs["store_path"] = self.store_path
            if "report_path" in obj_sig.parameters:
                partial_kwargs["report_path"] = self.report_path
            if "javascript_path" in obj_sig.parameters:
                partial_kwargs["javascript_path"] = self.javascript_path
            if "project_root" in obj_sig.parameters:
                partial_kwargs["project_root"] = self.project_root
            if "page_path" in obj_sig.parameters:
                partial_kwargs["page_path"] = self.page_path
            if "idstore" in obj_sig.parameters:
                partial_kwargs["idstore"] = self.idstore

            if len(partial_kwargs) > 0:
                return partial(obj, **partial_kwargs)
            else:
                return obj

        else:
            return obj

    @property
    def proxied_clases(self):
        return self._proxied_classes
