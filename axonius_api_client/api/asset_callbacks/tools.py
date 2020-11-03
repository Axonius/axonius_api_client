# -*- coding: utf-8 -*-
"""Tools for loading callbacks."""
from typing import Dict

from ...exceptions import ApiError
from ...tools import get_subcls
from .base import Base

CB_MAP: Dict[str, Base] = {
    Base.CB_NAME: Base,
    **{x.CB_NAME: x for x in get_subcls(cls=Base)},
}
"""Map of export name to callbacks class."""

CB_DEF: str = Base.CB_NAME


def get_callbacks_cls(export: str = CB_DEF) -> Base:
    """Get a callback class.

    Args:
        export: export format from asset object get method to map to a callback object
            must be one of :data:`CB_MAP`
    """
    export = export or CB_DEF
    if export in CB_MAP:
        return CB_MAP[export]
    raise ApiError(f"Invalid export {export!r}, valids: {list(CB_MAP)}")
