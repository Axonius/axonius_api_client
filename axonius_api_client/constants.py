# -*- coding: utf-8 -*-
"""Constants."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os
import sys

import six

from . import __package__ as PACKAGE_ROOT

MAX_PAGE_SIZE = 2000
""":obj:`int`: maximum page size that REST API allows"""

GUI_PAGE_SIZES = [25, 50, 100]
""":obj:`list` of :obj:`int`: valid page sizes for GUI paging"""

LOG_REQUEST_ATTRS_BRIEF = [
    "request to {request.url!r}",
    "method={request.method!r}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: request attributes to log when verbose=False"""

LOG_REQUEST_ATTRS_VERBOSE = [
    "request to {request.url!r}",
    "method={request.method!r}",
    "headers={request.headers}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: request attributes to log when verbose=True"""

LOG_RESPONSE_ATTRS_BRIEF = [
    "response from {response.url!r}",
    "method={response.request.method!r}",
    "status={response.status_code!r}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: response attributes to log when verbose=False"""

LOG_RESPONSE_ATTRS_VERBOSE = [
    "response from {response.url!r}",
    "method={response.request.method!r}",
    "headers={response.headers}",
    "status={response.status_code!r}",
    "reason={response.reason!r}",
    "elapsed={response.elapsed}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: response attributes to log when verbose=True"""

TIMEOUT_CONNECT = 5
""":obj:`int`: seconds to wait for connection to API."""

TIMEOUT_RESPONSE = 900
""":obj:`int`: seconds to wait for response from API."""

LOG_FMT_CONSOLE = "%(levelname)-8s [%(name)s] %(message)s"
""":obj:`str`: default logging format to use for console logs"""

LOG_FMT_FILE = "%(asctime)s %(levelname)-8s [%(name)s:%(funcName)s()] %(message)s"
""":obj:`str`: default logging format to use for file logs"""

LOG_DATEFMT_CONSOLE = "%m/%d/%Y %I:%M:%S %p"
""":obj:`str`: default datetime format to use for console logs"""

LOG_DATEFMT_FILE = "%m/%d/%Y %I:%M:%S %p"
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

LOG_LEVELS_INT_CSV = ", ".join([format(x) for x in LOG_LEVELS_INT])
""":obj:`str`: csv of valid logging level ints"""

LOG_FILE_PATH = os.getcwd()
""":obj:`str`: default path to use for log files"""

LOG_FILE_PATH_MODE = 0o700
""":obj:`str`: default permisisons to use when creating directories"""

LOG_FILE_NAME = "{pkg}.log".format(pkg=PACKAGE_ROOT)
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

CSV_FIELDS = {
    "device": ["id", "serial", "mac_address", "hostname", "name"],
    "user": ["id", "username", "mail", "name"],
    "sw": ["hostname", "installed_sw_name"],
}
""":obj:`dict`: mapping of csv required columns for csv types"""

SETTING_UNCHANGED = ["unchanged"]
""":obj:`list` of :obj:`str`: ref used by REST API when supplying a password
field that should remain the same as what is already in the database"""

DEFAULT_NODE = "master"
""":obj:`str`: default node name to use"""

CSV_KEYS_META = {
    "file": "file_path",
    "is_users_csv": "is_users",
    "is_installed_sw": "is_installed_sw",
    "id": "user_id",
    "csv_http": "resource_path",
    "csv_share": "resource_path",
    "csv_share_username": "username",
    "csv_share_password": "password",
}
""":obj:`dict`: mapping for csv adapter configuration items"""

CSV_ADAPTER = "csv"
""":obj:`str`: name of csv adapter"""

DEBUG_MATCHES = False
""":obj:`bool`: include log entries regarding match logic"""

DEFAULT_PERM = "ReadOnly"
""":obj:`str`: default user permission to use"""

VALID_PERMS = ["Restricted", "ReadWrite", "ReadOnly"]
""":obj:`list` of :obj:`str`: valid user permissions"""

COMPLEX = (dict, list, tuple)
""":obj:`tuple` of :obj:`type`: types that are considered as complex."""

EMPTY = [None, "", [], {}, ()]
""":obj:`list` of :obj:`type`: values that should be considered as empty"""

LIST = (tuple, list)
""":obj:`tuple` of :obj:`type`: types that are considered as lists"""

STR = six.string_types
""":obj:`tuple` of :obj:`type`: types that are considered as strings"""

INT = six.integer_types
""":obj:`tuple` of :obj:`type`: types that are considered as integers"""
BYTES = six.binary_type

SIMPLE = tuple(list(STR) + [int, bool, float])
""":obj:`tuple` of :obj:`type`: types that are considered as simple"""

SIMPLE_NONE = tuple(list(SIMPLE) + [None])
""":obj:`tuple` of :obj:`type`: types that are considered as simple or None"""

YES = [True, 1, "1", "true", "t", "yes", "y", "yas"]
""":obj:`list` of :obj:`type`: values that should be considered as truthy"""

NO = [False, 0, "0", "false", "f", "no", "n", "noes"]
""":obj:`list` of :obj:`type`: values that should be considered as falsey"""

PY36 = sys.version_info[0:2] >= (3, 6)
""":obj:`bool`: python version is 3.6 or higher"""

PY37 = sys.version_info[0:2] >= (3, 7)
""":obj:`bool`: python version is 3.7 or higher"""

CELL_MAX_LEN = 30000
CELL_MAX_STR = "...TRIMMED - {{c}} characters over max cell length {mc}"
CELL_MAX_STR = CELL_MAX_STR.format(mc=CELL_MAX_LEN)
CELL_JOINER = "\n"
