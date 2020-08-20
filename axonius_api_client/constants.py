# -*- coding: utf-8 -*-
"""Constants."""
import logging
import os
import pathlib
import sys
from typing import Dict, List, Optional, Tuple, Type, Union

import dotenv

from . import __package__ as PACKAGE_ROOT

DEFAULT_PATH = os.getcwd()

AX_ENV = os.environ.get("AX_ENV", "").strip() or DEFAULT_PATH


def load_dotenv(
    ax_env: str = AX_ENV, reenv: bool = False, verbose: bool = False
) -> Tuple[str, pathlib.Path]:
    """Pass."""
    if reenv:
        ax_env = os.environ.get("AX_ENV", "").strip() or DEFAULT_PATH

    ax_env_path = pathlib.Path(ax_env).expanduser().resolve()

    if ax_env_path.is_dir():
        ax_env_path = ax_env_path / ".env"

    return (
        dotenv.load_dotenv(dotenv_path=str(ax_env_path), verbose=verbose),
        ax_env_path,
    )


load_dotenv()

PY36: bool = sys.version_info[0:2] >= (3, 6)
""":obj:`bool`: python version is 3.6 or higher"""

PY37: bool = sys.version_info[0:2] >= (3, 7)
""":obj:`bool`: python version is 3.7 or higher"""

COMPLEX: Tuple[Type] = (dict, list, tuple)
""":obj:`tuple` of :obj:`type`: types that are considered as complex."""

SIMPLE: Tuple[Type] = (str, int, bool, float)
""":obj:`tuple` of :obj:`type`: types that are considered as simple"""

EMPTY: List[Union[str, list, dict, tuple]] = [None, "", [], {}, ()]
"""Values that should be considered as empty"""

YES: List[Union[bool, int, str]] = [True, 1, "1", "true", "t", "yes", "y", "on"]
"""Values that should be considered as truthy"""

NO: List[Union[bool, int, str]] = [False, 0, "0", "false", "f", "no", "n", "off"]
"""Values that should be considered as falsey"""

MAX_PAGE_SIZE: int = 2000
""":obj:`int`: maximum page size that REST API allows"""

PAGE_SIZE: int = MAX_PAGE_SIZE
PAGE_SLEEP: int = 0

GUI_PAGE_SIZES: List[int] = [25, 50, 100]
""":obj:`list` of :obj:`int`: valid page sizes for GUI paging"""

LOG_REQUEST_ATTRS_BRIEF: List[str] = [
    "request to {request.url!r}",
    "method={request.method!r}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: request attributes to log when verbose=False"""

RESPONSE_ATTR_MAP: dict = {
    "url": "{url!r}",
    "size": "{body_size}",
    "method": "{method!r}",
    "status": "{status_code!r}",
    "reason": "{reason!r}",
    "elapsed": "{elapsed}",
    "headers": "{headers}",
}

REQUEST_ATTR_MAP: dict = {
    "url": "{url!r}",
    "size": "{body_size}",
    "method": "{method!r}",
    "headers": "{headers}",
}

TIMEOUT_CONNECT: int = 5
""":obj:`int`: seconds to wait for connection to API."""

TIMEOUT_RESPONSE: int = 900
""":obj:`int`: seconds to wait for response from API."""

LOG_FMT_VERBOSE: str = (
    "%(asctime)s %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] %(message)s"
)
LOG_FMT_BRIEF: str = "%(levelname)-8s [%(name)s] %(message)s"

DEBUG: str = os.environ.get("AX_DEBUG", "").lower().strip()
DEBUG: bool = any([DEBUG == x for x in YES])

LOG_FMT_CONSOLE: str = LOG_FMT_VERBOSE if DEBUG else LOG_FMT_BRIEF
""":obj:`str`: default logging format to use for console logs"""

LOG_FMT_FILE: str = LOG_FMT_VERBOSE
""":obj:`str`: default logging format to use for file logs"""

LOG_DATEFMT_CONSOLE: str = "%m/%d/%Y %I:%M:%S %p %Z"
""":obj:`str`: default datetime format to use for console logs"""

LOG_DATEFMT_FILE: str = "%m/%d/%Y %I:%M:%S %p %Z"
""":obj:`str`: default datetime format to use for file logs"""

LOG_LEVEL_CONSOLE: str = "debug"
""":obj:`str`: default logging level to use for console log handlers"""

LOG_LEVEL_FILE: str = "debug"
""":obj:`str`: default logging level to use for file log handlers"""

LOG_LEVEL_HTTP: str = "debug"
""":obj:`str`: default logging level to use for :obj:`axonius_api_client.http.Http`"""

LOG_LEVEL_AUTH: str = "debug"
""":obj:`str`: default logging level to use for :obj:`axonius_api_client.auth.Mixins`"""

LOG_LEVEL_API: str = "debug"
""":obj:`str`: default logging level to use for
:obj:`axonius_api_client.api.mixins.Mixins`"""

LOG_LEVEL_WIZARD: str = "debug"

LOG_LEVEL_PACKAGE: str = "debug"
""":obj:`str`: default logging level to use for :mod:`axonius_api_client`"""

LOG_LEVELS_STR: List[str] = ["debug", "info", "warning", "error", "fatal"]
""":obj:`list` of :obj:`str`: valid logging level strs"""

LOG_LEVELS_STR_CSV: str = ", ".join(LOG_LEVELS_STR)
""":obj:`str`: csv of valid logging level strs"""

LOG_LEVELS_INT: List[int] = [getattr(logging, x.upper()) for x in LOG_LEVELS_STR]
""":obj:`list` of :obj:`int`: valid logging level ints"""

LOG_LEVELS_INT_CSV: str = ", ".join([str(x) for x in LOG_LEVELS_INT])
""":obj:`str`: csv of valid logging level ints"""

LOG_FILE_PATH: str = DEFAULT_PATH
""":obj:`str`: default path to use for log files"""

LOG_FILE_PATH_MODE: oct = 0o700
""":obj:`str`: default permisisons to use when creating directories"""

LOG_FILE_NAME: str = f"{PACKAGE_ROOT}.log"
""":obj:`str`: default log file name to use"""

LOG_FILE_MAX_MB: int = 5
""":obj:`int`: default rollover trigger in MB"""

LOG_FILE_MAX_FILES: int = 5
""":obj:`int`: default max rollovers to keep"""

LOG_NAME_STDERR: str = "handler_stderr"
""":obj:`str`: default handler name to use for STDERR log"""

LOG_NAME_STDOUT: str = "handler_stdout"
""":obj:`str`: default handler name to use for STDOUT log"""

LOG_NAME_FILE: str = "handler_file"
""":obj:`str`: default handler name to use for file log"""

SETTING_UNCHANGED: List[str] = ["unchanged"]
""":obj:`list` of :obj:`str`: ref used by REST API when supplying a password
field that should remain the same as what is already in the database"""

DEFAULT_NODE: str = "Master"
""":obj:`str`: default node name to use"""

CSV_ADAPTER: str = "csv"
""":obj:`str`: name of csv adapter"""
CSV_FIELD_NAME: str = "file_path"
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

FIELD_TRIM_LEN: int = 32000
FIELD_TRIM_STR: str = "...TRIMMED - {field_len} characters over {trim_len}"
FIELD_JOINER: str = "\n"
TABLE_FORMAT: str = "fancy_grid"
TABLE_MAX_ROWS: int = 5

OK_ARGS: dict = {"fg": "green", "bold": True, "err": True}

OK_TMPL: str = "** {msg}"

WARN_ARGS: dict = {"fg": "yellow", "bold": True, "err": True}

WARN_TMPL: str = "** WARNING: {msg}"

ERROR_ARGS: dict = {"fg": "red", "bold": True, "err": True}

ERROR_TMPL: str = "** ERROR: {msg}"
AGG_ADAPTER_NAME: str = "agg"
AGG_ADAPTER_TITLE: str = "Aggregated"
ALL_NAME: str = "all"
AGG_EXPR_FIELD_TYPE: str = "axonius"
AGG_ADAPTER_ALTS: List[str] = ["generic", "general", "specific", "agg", "aggregated"]
""":obj:`list` of :obj:`str`: list of alternatives for 'generic' adapter."""


NORM_TYPE_MAP: Tuple[Tuple[str, str, str, str], str] = (
    # (type, format, items.type, items.format), normalized
    (("string", "", "", ""), "string"),
    (("string", "date-time", "", ""), "string_datetime"),
    (("string", "image", "", ""), "string_image"),
    (("string", "version", "", ""), "string_version"),
    (("string", "ip", "", ""), "string_ipaddress"),
    (("string", "subnet", "", ""), "string_subnet"),
    (("bool", "", "", ""), "boolean"),
    (("integer", "", "", ""), "integer"),
    (("number", "", "", ""), "number"),
    (("array", "table", "array", ""), "list_table_object"),
    (("array", "", "array", ""), "list_object"),
    (("array", "", "integer", ""), "list_integer"),
    (("array", "", "number", ""), "list_number"),
    (("array", "", "string", ""), "list_string"),
    (("array", "", "string", "tag"), "list_string_tag"),
    (("array", "version", "string", "version"), "list_string_version"),
    (("array", "date-time", "string", "date-time"), "list_string_datetime"),
    (("array", "subnet", "string", "subnet"), "list_string_subnet"),
    (("array", "discrete", "string", "logo"), "list_string_discrete_logo"),
    (("array", "ip", "string", "ip"), "list_string_ipaddress"),
)


GET_SCHEMAS_KEYS: List[str] = ["name", "name_qual", "name_base"]
GET_SCHEMA_KEYS: List[str] = ["name_base", "name_qual", "name"]

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

MAX_BODY_LEN: int = 100000
GENERIC_NAME: str = "AdapterBase"
DISCOVERY_NAME: str = "DiscoverySchema"
CONFIG_TYPES: List[str] = ["generic", "specific", "discovery"]
KEY_MAP_CNX: List[Tuple[str, Optional[str], int]] = [
    ("adapter_name", "Adapter", 0),
    ("node_name", "Node", 0),
    ("id", "ID", 0),
    ("uuid", "UUID", 0),
    ("working", "Working", 0),
    ("error", "Error", 20),
    ("label", "Label", 0),
    ("schemas", None, 0),
]

KEY_MAP_ADAPTER: List[Tuple[str, Optional[str], int]] = [
    ("name", "Name", 0),
    ("node_name", "Node", 0),
    ("cnx_count_total", "Connections", 0),
    ("cnx_count_broken", "Broken", 0),
    ("cnx_count_working", "Working", 0),
]

KEY_MAP_SCHEMA: List[Tuple[str, Optional[str], int]] = [
    ("name", "Name", 0),
    ("title", "Title", 30),
    ("type", "Type", 0),
    ("required", "Required", 0),
    ("default", "Default", 0),
    ("description", "Description", 20),
    ("format", "Format", 0),
]
CNX_GONE: str = "Server is already gone, please try again after refreshing the page"
CNX_RETRY: int = 15
