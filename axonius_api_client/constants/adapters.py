# -*- coding: utf-8 -*-
"""Constants for adapters and adapter connections."""
from typing import Dict, List

CSV_ADAPTER: str = "csv"
"""name of csv adapter"""

CSV_FIELD_NAME: str = "file_path"
"""Field name used by CSV adapter for file."""

ALL_DEFAULTS: dict = {
    "http_proxy": None,
    "https_proxy": None,
    "verify_ssl": False,
}
FILE_DEFAULTS: dict = {
    "azure_blob_name": None,
    "azure_connection_string": None,
    "azure_storage_container_name": None,
    "custom_prefix": None,
    "encoding": None,
    "ignore_encoding_errors": False,
    "is_installed_sw": False,
    "is_users": False,
    "list_field_separator": None,
    "password": None,
    "request_headers": None,
    "resource_path": None,
    "s3_access_key_id": None,
    "s3_bucket": None,
    "s3_object_location": None,
    "s3_secret_access_key": None,
    "s3_use_ec2_attached_instance_profile": False,
    "username": None,
    **ALL_DEFAULTS,
}
CNX_SANE_DEFAULTS: Dict[str, dict] = {
    "all": ALL_DEFAULTS,
    "csv": FILE_DEFAULTS,
    "json": FILE_DEFAULTS,
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

INGESTION_NAME: str = "IngestionRulesSchema"

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
# """Tablize map of field name to user-friendly title for adapter connections."""

# KEY_MAP_ADAPTER: List[Tuple[str, Optional[str], int]] = [
#     ("name", "Name", 0),
#     ("node_name", "Node", 0),
#     ("cnx_count_total", "Connections", 0),
#     ("cnx_count_broken", "Broken", 0),
#     ("cnx_count_working", "Working", 0),
#     ("cnx_count_inactive", "Inactive", 0),
# ]
# """Tablize map of field name to user-friendly title for adapters."""

# KEY_MAP_SCHEMA: List[Tuple[str, Optional[str], int]] = [
#     ("name", "Name", 0),
#     ("title", "Title", 30),
#     ("type", "Type", 0),
#     ("required", "Required", 0),
#     ("default", "Default", 0),
#     ("description", "Description", 20),
#     ("format", "Format", 0),
# ]
# """Tablize map of field name to user-friendly title for config schemas."""

CNX_GONE: str = "Server is already gone, please try again after refreshing the page"
"""Message to print when an adapter connection disappears"""

CNX_RETRY: int = 15
"""Number of times to retry fetching a connection"""
