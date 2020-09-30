# -*- coding: utf-8 -*-
"""Constants."""
import logging
import os
import pathlib
import sys
from typing import Dict, List, Optional, Tuple, Type, Union

import dotenv

from . import __package__ as PACKAGE_ROOT

DEFAULT_PATH: str = os.getcwd()
"""Default path to use throughout this package"""

AX_ENV_KEY: str = "AX_ENV"
"""Environment variable to use to override path to '.env' file"""


def load_dotenv(
    ax_env: Union[str, pathlib.Path] = DEFAULT_PATH, **kwargs
) -> Tuple[str, pathlib.Path]:
    """Load a '.env' file as environment variables accessible to this package.

    Args:
        ax_env: path to .env file to load, if directory will look for '.env' in that directory
        **kwargs: passed to dotenv.load_dotenv()
    """
    ax_env = os.environ.get(AX_ENV_KEY, "").strip() or ax_env
    ax_env_path = pathlib.Path(ax_env).expanduser().resolve()
    if ax_env_path.is_dir():
        ax_env_path = ax_env_path / ".env"
    return (
        dotenv.load_dotenv(dotenv_path=str(ax_env_path), **kwargs),
        ax_env_path,
    )


load_dotenv()

PY36: bool = sys.version_info[0:2] >= (3, 6)
"""python version is 3.6 or higher"""

PY37: bool = sys.version_info[0:2] >= (3, 7)
"""python version is 3.7 or higher"""

COMPLEX: Tuple[Type] = (dict, list, tuple)
"""types that are considered as complex."""

SIMPLE: Tuple[Type] = (str, int, bool, float)
"""types that are considered as simple"""

EMPTY: List[Union[str, list, dict, tuple]] = [None, "", [], {}, ()]
"""Values that should be considered as empty"""

YES: List[Union[bool, int, str]] = [True, 1, "1", "true", "t", "yes", "y", "on"]
"""Values that should be considered as truthy"""

NO: List[Union[bool, int, str]] = [False, 0, "0", "false", "f", "no", "n", "off"]
"""Values that should be considered as falsey"""

MAX_PAGE_SIZE: int = 2000
"""maximum page size that REST API allows"""

PAGE_SIZE: int = MAX_PAGE_SIZE
"""API wide default page size to use."""

PAGE_SLEEP: int = 0
"""API wide default number of seconds to sleep between in page."""

GUI_PAGE_SIZES: List[int] = [25, 50, 100]
"""valid page sizes for GUI paging"""

RESPONSE_ATTR_MAP: dict = {
    "url": "{url!r}",
    "size": "{body_size}",
    "method": "{method!r}",
    "status": "{status_code!r}",
    "reason": "{reason!r}",
    "elapsed": "{elapsed}",
    "headers": "{headers}",
}
"""Mapping of response attributes to log to their formatting strings."""

REQUEST_ATTR_MAP: dict = {
    "url": "{url!r}",
    "size": "{body_size}",
    "method": "{method!r}",
    "headers": "{headers}",
}
"""Mapping of request attributes to log to their formatting strings."""

TIMEOUT_CONNECT: int = 5
"""seconds to wait for connection to API."""

TIMEOUT_RESPONSE: int = 900
"""seconds to wait for response from API."""

LOG_FMT_VERBOSE: str = (
    "%(asctime)s %(levelname)-8s [%(name)s:%(funcName)s:%(pathname)s:%(lineno)d] " "%(message)s"
)
"""Logging format to use for verbose logging."""

LOG_FMT_BRIEF: str = "%(levelname)-8s %(module)-15s %(message)s"
"""Logging format to use for brief logging."""

DEBUG: str = os.environ.get("AX_DEBUG", "").lower().strip()
DEBUG: bool = any([DEBUG == x for x in YES])
"""Enable API wide debug logging, looks at environment variable AX_DEBUG."""

LOG_FMT_CONSOLE: str = LOG_FMT_VERBOSE if DEBUG else LOG_FMT_BRIEF
"""default logging format for console logs, will be verbose if :attr:`DEBUG` is true"""

LOG_FMT_FILE: str = LOG_FMT_VERBOSE
"""default logging format for file logs"""

LOG_DATEFMT_CONSOLE: str = "%m/%d/%Y %I:%M:%S %p %Z"
"""default datetime format for console logs"""

LOG_DATEFMT_FILE: str = "%m/%d/%Y %I:%M:%S %p %Z"
"""default datetime format for file logs"""

LOG_LEVEL_CONSOLE: str = "debug"
"""default logging level for console log handlers"""

LOG_LEVEL_FILE: str = "debug"
"""default logging level for file log handlers"""

LOG_LEVEL_HTTP: str = "debug"
"""default logging level for :obj:`axonius_api_client.http.Http`"""

LOG_LEVEL_AUTH: str = "debug"
"""default logging level for :obj:`axonius_api_client.auth.models.Mixins`"""

LOG_LEVEL_API: str = "debug"
"""default logging level for :obj:`axonius_api_client.api.mixins.ModelMixins`"""

LOG_LEVEL_WIZARD: str = "info"
"""default logging level for :obj:`axonius_api_client.api.wizard.wizard.Wizard`"""

LOG_LEVEL_PACKAGE: str = "debug"
"""default logging level for the entire package"""

LOG_LEVELS_STR: List[str] = ["debug", "info", "warning", "error", "fatal"]
"""list of valid logging level strs"""

LOG_LEVELS_STR_CSV: str = ", ".join(LOG_LEVELS_STR)
"""csv of valid logging level strs"""

LOG_LEVELS_INT: List[int] = [getattr(logging, x.upper()) for x in LOG_LEVELS_STR]
"""list of valid logging level ints"""

LOG_LEVELS_INT_CSV: str = ", ".join([str(x) for x in LOG_LEVELS_INT])
"""csv of valid logging level ints"""

LOG_FILE_PATH: str = DEFAULT_PATH
"""default path for log files"""

LOG_FILE_PATH_MODE = 0o700
""":obj:`oct` default permisisons to use when creating directories"""

LOG_FILE_NAME: str = f"{PACKAGE_ROOT}.log"
"""default log file name to use"""

LOG_FILE_MAX_MB: int = 5
"""default rollover trigger in MB"""

LOG_FILE_MAX_FILES: int = 5
"""default max rollovers to keep"""

LOG_NAME_STDERR: str = "handler_stderr"
"""default handler name for STDERR log"""

LOG_NAME_STDOUT: str = "handler_stdout"
"""default handler name for STDOUT log"""

LOG_NAME_FILE: str = "handler_file"
"""default handler name for file log"""

SETTING_UNCHANGED: List[str] = ["unchanged"]
"""used by REST API when supplying a password field that is the same in the database"""

DEFAULT_NODE: str = "Master"
"""default node name to use"""

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

FIELD_TRIM_LEN: int = 32000
"""Default length to trim field values to"""

FIELD_TRIM_STR: str = "...TRIMMED - {field_len} characters over {trim_len}"
"""String to append to trimmed field values"""

FIELD_JOINER: str = "\n"
"""String to use to join field values that are lists"""

TABLE_FORMAT: str = "fancy_grid"
"""Default tablize export format."""

TABLE_MAX_ROWS: int = 5
"""Default row limit for tablize export"""

OK_ARGS: dict = {"fg": "green", "bold": True, "err": True}
"""default arguments for echo_ok"""

OK_TMPL: str = "** {msg}"
"""default template for echo_ok"""

WARN_ARGS: dict = {"fg": "yellow", "bold": True, "err": True}
"""default arguments for echo_warn"""

WARN_TMPL: str = "** WARNING: {msg}"
"""default template for echo_warn"""

ERROR_ARGS: dict = {"fg": "red", "bold": True, "err": True}
"""default arguments for echo_error"""

ERROR_TMPL: str = "** ERROR: {msg}"
"""default template for echo_error"""

AGG_ADAPTER_NAME: str = "agg"
"""Short name to use for aggregated adapter"""

AGG_ADAPTER_TITLE: str = "Aggregated"
"""Title to use for aggregated adapter"""

ALL_NAME: str = "all"
"""alternative name to use for 'all' field."""

AGG_EXPR_FIELD_TYPE: str = "axonius"
"""epxr_field_type to use in saved query expressions for aggregated fields"""

AGG_ADAPTER_ALTS: List[str] = ["generic", "general", "specific", "agg", "aggregated"]
"""list of list of alternatives for 'generic' adapter."""

GET_SCHEMAS_KEYS: List[str] = ["name", "name_qual", "name_base", "title"]
"""field schema keys to check when finding field schemas"""

GET_SCHEMA_KEYS: List[str] = ["name_base", "name_qual", "name", "title"]
"""field schema keys to check when finding a single field schema"""

FUZZY_SCHEMAS_KEYS: List[str] = ["name_base", "title"]
"""field schema keys to check when fuzzy matching field schemas"""

SCHEMAS_CUSTOM: Dict[str, dict] = {
    "report_adapters_missing": {
        "adapters_missing": {
            "adapter_name": "report",
            "column_name": "report:adapters_missing",
            "column_title": "Report: Adapters Missing",
            "is_complex": False,
            "is_list": True,
            "is_root": True,
            "parent": "root",
            "name": "adapters_missing",
            "name_base": "adapters_missing",
            "name_qual": "adapters_missing",
            "title": "Adapters Missing",
            "type": "string",
            "type_norm": "list_string",
            "is_custom": True,
        }
    },
    "report_software_whitelist": {
        "software_missing": {
            "adapter_name": "report",
            "column_name": "report:software_missing",
            "column_title": "Report: Missing Software",
            "is_complex": False,
            "is_list": True,
            "is_root": True,
            "parent": "root",
            "name": "software_missing",
            "name_base": "software_missing",
            "name_qual": "software_missing",
            "title": "Missing Software",
            "type": "string",
            "type_norm": "list_string",
            "is_custom": True,
        },
        "software_extra": {
            "adapter_name": "report",
            "column_name": "report:software_extra",
            "column_title": "Report: Extra Software",
            "is_complex": False,
            "is_list": True,
            "is_root": True,
            "parent": "root",
            "name": "software_extra",
            "name_base": "software_extra",
            "name_qual": "software_extra",
            "title": "Extra Software",
            "type": "string",
            "type_norm": "list_string",
            "is_custom": True,
        },
        "software_whitelist": {
            "adapter_name": "report",
            "column_name": "report:software_whitelist",
            "column_title": "Report: Software Whitelist",
            "is_complex": False,
            "is_list": True,
            "is_root": True,
            "parent": "root",
            "name": "software_whitelist",
            "name_base": "software_whitelist",
            "name_qual": "software_whitelist",
            "title": "Software Whitelist",
            "type": "string",
            "type_norm": "list_string",
            "is_custom": True,
        },
    },
}
"""custom schemas for reports in asset callbacks"""

MAX_BODY_LEN: int = 100000
"""maximum body length to trim when printing request/response bodies"""

GENERIC_NAME: str = "AdapterBase"
"""name of generic adapter advanced settings in adapter schemas"""

DISCOVERY_NAME: str = "DiscoverySchema"
"""name of discover adapter advanced settings in adapter schemas"""

CONFIG_TYPES: List[str] = ["generic", "specific", "discovery"]
"""valid names of types of adapter advanced settings"""

KEY_MAP_CNX: List[Tuple[str, Optional[str], int]] = [
    ("adapter_name", "Adapter", 0),
    ("node_name", "Node", 0),
    ("id", "ID", 0),
    ("uuid", "UUID", 0),
    ("working", "Working", 0),
    ("error", "Error", 20),
    ("connection_label", "Connection Label", 0),
    ("schemas", None, 0),
]
"""Tablize map of field name to user friendly title for adapter connections."""

KEY_MAP_ADAPTER: List[Tuple[str, Optional[str], int]] = [
    ("name", "Name", 0),
    ("node_name", "Node", 0),
    ("cnx_count_total", "Connections", 0),
    ("cnx_count_broken", "Broken", 0),
    ("cnx_count_working", "Working", 0),
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

CNX_GONE: str = "Server is already gone, please try again after refreshing the page"
"""Message to print when an adapter connection disappears"""

CNX_RETRY: int = 15
"""Number of times to retry fetching a connection"""
