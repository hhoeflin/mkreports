import inspect
from functools import partial
from pathlib import Path
from typing import Callable, Optional, Union

from . import md


class MdProxy:
    def __init__(
        self,
        store_path: Path,
        report_path: Path,
        datatable_id: Optional[Union[str, Callable[[str], str]]] = None,
        altair_id: Optional[Union[str, Callable[[str], str]]] = None,
    ):
        self.store_path = store_path
        self.report_path = report_path
        self.datatable_id = datatable_id
        self.altair_id = altair_id

    def __getattr__(self, name):
        # we are not checking if it is included; if not, should raise error
        obj = getattr(md, name)

        # if is a class; try to fix the init method
        if inspect.isclass(obj):
            # check the init method signature
            partial_kwargs = {}
            obj_sig = inspect.signature(obj)
            if "store_path" in obj_sig.parameters:
                partial_kwargs["store_path"] = self.store_path
            if "report_path" in obj_sig.parameters:
                partial_kwargs["report_path"] = self.report_path

            if (
                self.datatable_id is not None
                and name == "DataTable"
                and "table_id" in obj_sig.parameters
            ):
                partial_kwargs["table_id"] = self.datatable_id

            if (
                self.altair_id is not None
                and name == "Altair"
                and "altair_id" in obj_sig.parameters
            ):
                partial_kwargs["altair_id"] = self.altair_id

            if len(partial_kwargs) > 0:
                return partial(obj, **partial_kwargs)
            else:
                return obj

        else:
            return obj
