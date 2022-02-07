# -*- coding: utf-8 -*-
"""Constants for adapters and adapter connections."""
from typing import List, Optional, Tuple

KEY_MAP_CNX: List[Tuple[str, Optional[str], int]] = [
    ("id", "ID", 0),
    ("uuid", "UUID", 0),
    ("working", "Working", 0),
    ("active", "Active", 0),
    ("connection_label", "Label", 0),
    ("schemas", None, 0),
]
"""Tablize map of field name to user friendly title for adapter connections."""

KEY_MAP_ADAPTER: List[Tuple[str, Optional[str], int]] = [
    ("name", "Name", 0),
    ("title", "Title", 15),
    ("node_name", "Node", 0),
    ("cnx_count_total", "Connections", 0),
    ("cnx_count_broken", "Broken", 0),
    ("cnx_count_working", "Working", 0),
    ("cnx_count_inactive", "Inactive", 0),
]
"""Tablize map of field name to user friendly title for adapters."""

KEY_MAP_SCHEMA: List[Tuple[str, Optional[str], int]] = [
    ("name", "Name", 0),
    ("title", "Title", 30),
    ("type", "Type", 0),
    ("required", "Required", 0),
    ("default", "Default", 0),
    ("description", "Description", 20),
    ("format", "Format", 0),
]
"""Tablize map of field name to user friendly title for config schemas."""
