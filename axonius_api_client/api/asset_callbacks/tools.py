# -*- coding: utf-8 -*-
"""Asset export callbacks."""
from typing import Dict, Optional

from ...exceptions import ApiError
from .base import Base
from .base_csv import Csv
from .base_json import Json
from .base_json_to_csv import JsonToCsv
from .base_table import Table
from .base_xlsx import Xlsx

DEFAULT_CALLBACKS_CLS: str = "base"
"""Default callback object to use"""

CALLBACKS_MAP: Dict[str, Base] = {
    "json": Json,
    "csv": Csv,
    "table": Table,
    "base": Base,
    "json_to_csv": JsonToCsv,
    "xlsx": Xlsx,
}


def get_callbacks_cls(export: Optional[str] = None) -> Base:
    """Get a callback class.

    Args:
        export: export format from asset object get method to map to a callback object
    """
    export = export or DEFAULT_CALLBACKS_CLS
    if export in CALLBACKS_MAP:
        return CALLBACKS_MAP[export]
    raise ApiError(f"Invalid export {export!r}, valids: {list(CALLBACKS_MAP)}")
