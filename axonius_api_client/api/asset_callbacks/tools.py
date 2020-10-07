# -*- coding: utf-8 -*-
"""Tools for loading callbacks."""
from typing import Dict

from ...constants.api import DEFAULT_CALLBACKS_CLS
from ...exceptions import ApiError
from ...tools import get_subcls
from .base import Base

CALLBACKS_MAP: Dict[str, Base] = {
    Base.CB_NAME: Base,
    **{x.CB_NAME: x for x in get_subcls(cls=Base)},
}
"""Map of export name to callbacks class."""


def get_callbacks_cls(export: str = DEFAULT_CALLBACKS_CLS) -> Base:
    """Get a callback class.

    Args:
        export: export format from asset object get method to map to a callback object
            must be one of :data:`CALLBACKS_MAP`
    """
    export = export or DEFAULT_CALLBACKS_CLS
    if export in CALLBACKS_MAP:
        return CALLBACKS_MAP[export]
    raise ApiError(f"Invalid export {export!r}, valids: {list(CALLBACKS_MAP)}")
