import inspect
from functools import partial, update_wrapper
from typing import Any, Dict, Optional

from .settings import PageInfo


def register_md(name):
    def register_md_named(cls):
        MdProxy._proxied_classes[name] = cls
        return cls

    return register_md_named


class MdProxy:
    """
    Proxies the MdObj objects

    Makes the MdObj available with PageInfo prefilled.
    """

    _proxied_classes: Dict[str, Any] = dict()

    def __init__(
        self,
        page_info: PageInfo,
        md_defaults: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Initialize the proxy.

        Args:
            page_info (PageInfo): The info of the page for which the proxy works.
            md_defaults (Optional[Dict[str, Dict[str, Any]]): A dictionary mapping the names
                md objects (accessed from the proxy) to default keywords included when
                they are being called.
        """
        self.page_info = page_info
        self.md_defaults = md_defaults if md_defaults is not None else {}

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

            # check if there are defaults for the md-object
            if name in self.md_defaults:
                partial_kwargs.update(self.md_defaults[name])

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
    def proxied_classes(self) -> Dict[str, Any]:
        """
        Returns:
            Dict[str, Any]: A dict with the registered items under their name.
        """
        return self._proxied_classes
