# -*- coding: utf-8 -*-
"""Constants."""
import logging
import os
import pathlib
import sys

import dotenv

from . import __package__ as PACKAGE_ROOT

DEFAULT_PATH = os.getcwd()

AX_ENV = os.environ.get("AX_ENV", "").strip() or DEFAULT_PATH


def load_dotenv(ax_env=AX_ENV, reenv=False, verbose=False):
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

PY36 = sys.version_info[0:2] >= (3, 6)
""":obj:`bool`: python version is 3.6 or higher"""

PY37 = sys.version_info[0:2] >= (3, 7)
""":obj:`bool`: python version is 3.7 or higher"""

COMPLEX = (dict, list, tuple)
""":obj:`tuple` of :obj:`type`: types that are considered as complex."""

SIMPLE = (str, int, bool, float)
""":obj:`tuple` of :obj:`type`: types that are considered as simple"""

EMPTY = [None, "", [], {}, ()]
""":obj:`list` of :obj:`type`: values that should be considered as empty"""

YES = [True, 1, "1", "true", "t", "yes", "y"]
""":obj:`list` of :obj:`type`: values that should be considered as truthy"""

NO = [False, 0, "0", "false", "f", "no", "n"]
""":obj:`list` of :obj:`type`: values that should be considered as falsey"""

MAX_PAGE_SIZE = 2000
""":obj:`int`: maximum page size that REST API allows"""

PAGE_SIZE = MAX_PAGE_SIZE
PAGE_SLEEP = 0
PAGE_CACHE = False

GUI_PAGE_SIZES = [25, 50, 100]
""":obj:`list` of :obj:`int`: valid page sizes for GUI paging"""

LOG_REQUEST_ATTRS_BRIEF = [
    "request to {request.url!r}",
    "method={request.method!r}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: request attributes to log when verbose=False"""

RESPONSE_ATTR_MAP = {
    "url": "{response.url!r}",
    "size": "{response.body_size}",
    "method": "{response.request.method!r}",
    "status": "{response.status_code!r}",
    "reason": "{response.reason!r}",
    "elapsed": "{response.elapsed}",
    "headers": "{response.headers}",
}

REQUEST_ATTR_MAP = {
    "url": "{request.url!r}",
    "size": "{request.body_size}",
    "method": "{request.method!r}",
    "headers": "{request.headers}",
}

TIMEOUT_CONNECT = 5
""":obj:`int`: seconds to wait for connection to API."""

TIMEOUT_RESPONSE = 900
""":obj:`int`: seconds to wait for response from API."""

LOG_FMT_VERBOSE = (
    "%(asctime)s %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] %(message)s"
)
LOG_FMT_BRIEF = "%(levelname)-8s [%(name)s] %(message)s"

DEBUG = os.environ.get("AX_DEBUG", "").lower().strip()
DEBUG = any([DEBUG == x for x in YES])

LOG_FMT_CONSOLE = LOG_FMT_VERBOSE if DEBUG else LOG_FMT_BRIEF
""":obj:`str`: default logging format to use for console logs"""

LOG_FMT_FILE = LOG_FMT_VERBOSE
""":obj:`str`: default logging format to use for file logs"""

LOG_DATEFMT_CONSOLE = "%m/%d/%Y %I:%M:%S %p %Z"
""":obj:`str`: default datetime format to use for console logs"""

LOG_DATEFMT_FILE = "%m/%d/%Y %I:%M:%S %p %Z"
""":obj:`str`: default datetime format to use for file logs"""

LOG_LEVEL_CONSOLE = "debug"
""":obj:`str`: default logging level to use for console log handlers"""

LOG_LEVEL_FILE = "debug"
""":obj:`str`: default logging level to use for file log handlers"""

LOG_LEVEL_HTTP = "debug"
""":obj:`str`: default logging level to use for :obj:`axonius_api_client.http.Http`"""

LOG_LEVEL_AUTH = "debug"
""":obj:`str`: default logging level to use for :obj:`axonius_api_client.auth.Mixins`"""

LOG_LEVEL_API = "debug"
""":obj:`str`: default logging level to use for
:obj:`axonius_api_client.api.mixins.Mixins`"""

LOG_LEVEL_PACKAGE = "debug"
""":obj:`str`: default logging level to use for :mod:`axonius_api_client`"""

LOG_LEVELS_STR = ["debug", "info", "warning", "error", "fatal"]
""":obj:`list` of :obj:`str`: valid logging level strs"""

LOG_LEVELS_STR_CSV = ", ".join(LOG_LEVELS_STR)
""":obj:`str`: csv of valid logging level strs"""

LOG_LEVELS_INT = [getattr(logging, x.upper()) for x in LOG_LEVELS_STR]
""":obj:`list` of :obj:`int`: valid logging level ints"""

LOG_LEVELS_INT_CSV = ", ".join([str(x) for x in LOG_LEVELS_INT])
""":obj:`str`: csv of valid logging level ints"""

LOG_FILE_PATH = DEFAULT_PATH
""":obj:`str`: default path to use for log files"""

LOG_FILE_PATH_MODE = 0o700
""":obj:`str`: default permisisons to use when creating directories"""

LOG_FILE_NAME = f"{PACKAGE_ROOT}.log"
""":obj:`str`: default log file name to use"""

LOG_FILE_MAX_MB = 5
""":obj:`int`: default rollover trigger in MB"""

LOG_FILE_MAX_FILES = 5
""":obj:`int`: default max rollovers to keep"""

LOG_NAME_STDERR = "handler_stderr"
""":obj:`str`: default handler name to use for STDERR log"""

LOG_NAME_STDOUT = "handler_stdout"
""":obj:`str`: default handler name to use for STDOUT log"""

LOG_NAME_FILE = "handler_file"
""":obj:`str`: default handler name to use for file log"""

SETTING_UNCHANGED = ["unchanged"]
""":obj:`list` of :obj:`str`: ref used by REST API when supplying a password
field that should remain the same as what is already in the database"""

DEFAULT_NODE = "Master"
""":obj:`str`: default node name to use"""

CSV_ADAPTER = "csv"
""":obj:`str`: name of csv adapter"""
CSV_FIELD_NAME = "file_path"
CNX_SANE_DEFAULTS = {
    "all": {"verify_ssl": False},
    "csv": {
        "is_users": False,
        "is_installed_sw": False,
        "s3_use_ec2_attached_instance_profile": False,
        "verify_ssl": False,
    },
}
DEFAULT_PERM = "ReadOnly"
""":obj:`str`: default user permission to use"""

VALID_PERMS = ["Restricted", "ReadWrite", "ReadOnly"]
""":obj:`list` of :obj:`str`: valid user permissions"""
PERM_SETS = [
    "Adapters",
    "Dashboard",
    "Devices",
    "Enforcements",
    "Instances",
    "Reports",
    "Settings",
    "Users",
]

FIELD_TRIM_LEN = 32000
FIELD_TRIM_STR = "...TRIMMED - {field_len} characters over {trim_len}"
FIELD_JOINER = "\n"
TABLE_FORMAT = "fancy_grid"
TABLE_MAX_ROWS = 5

OK_ARGS = {"fg": "green", "bold": True, "err": True}

OK_TMPL = "** {msg}"

WARN_ARGS = {"fg": "yellow", "bold": True, "err": True}

WARN_TMPL = "** WARNING: {msg}"

ERROR_ARGS = {"fg": "red", "bold": True, "err": True}

ERROR_TMPL = "** ERROR: {msg}"
AGG_ADAPTER_NAME = "agg"
AGG_ADAPTER_TITLE = "Aggregated"
ALL_NAME = "all"
AGG_ADAPTER_ALTS = ["generic", "general", "specific", "agg", "aggregated"]
""":obj:`list` of :obj:`str`: list of alternatives for 'generic' adapter."""


NORM_TYPE_MAP = (
    # (type, format, items.type, items.format), normalized
    (("string", "", "", ""), "string"),
    (("string", "date-time", "", ""), "string_datetime"),
    (("string", "image", "", ""), "string_image"),
    (("string", "version", "", ""), "string_version"),
    (("string", "ip", "", ""), "string_ipaddress"),
    (("bool", "", "", ""), "bool"),
    (("integer", "", "", ""), "integer"),
    (("number", "", "", ""), "number"),
    (("array", "table", "array", ""), "complex_table"),
    (("array", "", "array", ""), "complex"),
    (("array", "", "integer", ""), "list_integer"),
    (("array", "", "string", ""), "list_string"),
    (("array", "", "string", "tag"), "list_string"),
    (("array", "version", "string", "version"), "list_string_version"),
    (("array", "date-time", "string", "date-time"), "list_string_datetime"),
    (("array", "subnet", "string", "subnet"), "list_string_subnet"),
    (("array", "discrete", "string", "logo"), "list_string"),
    (("array", "ip", "string", "ip"), "list_string_ipaddress"),
)


GET_SCHEMAS_KEYS = ["name", "name_qual", "name_base"]
GET_SCHEMA_KEYS = ["name_base", "name_qual", "name"]

SCHEMAS_CUSTOM = {
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
    }
}

MAX_BODY_LEN = 2000
GENERIC_NAME = "AdapterBase"


KEY_MAP_CNX = [
    ("adapter_name", "Adapter", 0),
    ("node_name", "Node", 0),
    ("id", "ID", 0),
    ("uuid", "UUID", 0),
    ("working", "Working", 0),
    ("error", "Error", 20),
    ("label", "Label", 0),
    ("schemas", None, 0),
]

KEY_MAP_ADAPTER = [
    ("name", "Name", 0),
    ("node_name", "Node", 0),
    ("cnx_count_total", "Connections", 0),
    ("cnx_count_broken", "Broken", 0),
    ("cnx_count_working", "Working", 0),
]

KEY_MAP_SCHEMA = [
    ("name", "Name", 0),
    ("title", "Title", 30),
    ("type", "Type", 0),
    ("required", "Required", 0),
    ("default", "Default", 0),
    ("description", "Description", 20),
    ("format", "Format", 0),
]
CNX_GONE = "Server is already gone, please try again after refreshing the page"
CNX_RETRY = 15
