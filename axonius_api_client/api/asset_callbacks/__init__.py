# -*- coding: utf-8 -*-
"""API models package."""
from ...exceptions import ApiError
from . import base, base_csv, base_json, base_table
from .base import Base
from .base_csv import Csv
from .base_json import Json
from .base_json_to_csv import JsonToCsv
from .base_table import Table

__all__ = (
    "Base",
    "Csv",
    "Json",
    "Table",
    "base",
    "base_csv",
    "base_json",
    "base_table",
)


DEFAULT_CALLBACKS_CLS = "base"
CALLBACKS_MAP = {
    "json": Json,
    "csv": Csv,
    "table": Table,
    "base": Base,
    "json_to_csv": JsonToCsv,
}


def get_callbacks_cls(export=None):
    """Get a callback class."""
    export = export or DEFAULT_CALLBACKS_CLS
    if export in CALLBACKS_MAP:
        return CALLBACKS_MAP[export]
    raise ApiError(f"Invalid export {export!r}, valids: {list(CALLBACKS_MAP)}")
