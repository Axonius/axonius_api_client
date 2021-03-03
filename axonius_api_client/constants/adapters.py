# -*- coding: utf-8 -*-
"""Constants for adapters and adapter connections."""
from typing import Dict, List

CSV_ADAPTER: str = "csv"
"""name of csv adapter"""

CSV_FIELD_NAME: str = "file_path"
"""Field name used by CSV adapter for file."""

CNX_SANE_DEFAULTS: Dict[str, dict] = {
    "all": {"verify_ssl": False},
    "csv": {
        "is_users": False,
        "is_installed_sw": False,
        "s3_use_ec2_attached_instance_profile": False,
        "verify_ssl": False,
    },
    "json": {
        "is_users": False,
        "is_installed_sw": False,
        "s3_use_ec2_attached_instance_profile": False,
        "verify_ssl": False,
    },
}
"""Sane connection defaults for adapters."""
CNX_LABEL_SCHEMA = {
    "name": "connection_label",
    "title": "Connection Label",
    "type": "string",
    "required": False,
}
GENERIC_NAME: str = "AdapterBase"
"""name of generic adapter advanced settings in adapter schemas"""

DISCOVERY_NAME: str = "DiscoverySchema"
"""name of discover adapter advanced settings in adapter schemas"""

CONFIG_TYPES: List[str] = ["generic", "specific", "discovery"]
"""valid names of types of adapter advanced settings"""

# KEY_MAP_CNX: List[Tuple[str, Optional[str], int]] = [
#     ("adapter_name", "Adapter", 0),
#     ("node_name", "Node", 0),
#     ("id", "ID", 0),
#     ("uuid", "UUID", 0),
#     ("working", "Working", 0),
#     ("error", "Error", 20),
#     ("connection_label", "Connection Label", 0),
#     ("schemas", None, 0),
# ]
# """Tablize map of field name to user friendly title for adapter connections."""

# KEY_MAP_ADAPTER: List[Tuple[str, Optional[str], int]] = [
#     ("name", "Name", 0),
#     ("node_name", "Node", 0),
#     ("cnx_count_total", "Connections", 0),
#     ("cnx_count_broken", "Broken", 0),
#     ("cnx_count_working", "Working", 0),
#     ("cnx_count_inactive", "Inactive", 0),
# ]
# """Tablize map of field name to user friendly title for adapters."""

# KEY_MAP_SCHEMA: List[Tuple[str, Optional[str], int]] = [
#     ("name", "Name", 0),
#     ("title", "Title", 30),
#     ("type", "Type", 0),
#     ("required", "Required", 0),
#     ("default", "Default", 0),
#     ("description", "Description", 20),
#     ("format", "Format", 0),
# ]
# """Tablize map of field name to user friendly title for config schemas."""

CNX_GONE: str = "Server is already gone, please try again after refreshing the page"
"""Message to print when an adapter connection disappears"""

CNX_RETRY: int = 15
"""Number of times to retry fetching a connection"""
