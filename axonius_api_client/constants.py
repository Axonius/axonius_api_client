# -*- coding: utf-8 -*-
"""Constants for this package."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os
import sys

import six

from . import __package__ as PACKAGE_ROOT

MAX_PAGE_SIZE = 2000
""":obj:`int`: Maximum page size that REST API allows."""

GUI_PAGE_SIZES = [25, 50, 100]
""":obj:`list` of :obj:`int`: Valid page sizes for GUI paging."""

LOG_REQUEST_ATTRS_BRIEF = [
    "request to {request.url!r}",
    "method={request.method!r}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: Request attributes to log when verbose=False."""

LOG_REQUEST_ATTRS_VERBOSE = [
    "request to {request.url!r}",
    "method={request.method!r}",
    "headers={request.headers}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: Request attributes to log when verbose=True."""

LOG_RESPONSE_ATTRS_BRIEF = [
    "response from {response.url!r}",
    "method={response.request.method!r}",
    "status={response.status_code!r}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: Response attributes to log when verbose=False."""

LOG_RESPONSE_ATTRS_VERBOSE = [
    "response from {response.url!r}",
    "method={response.request.method!r}",
    "headers={response.headers}",
    "status={response.status_code!r}",
    "reason={response.reason!r}",
    "elapsed={response.elapsed}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: Response attributes to log when verbose=True."""

LOG_FMT_CONSOLE = "%(levelname)-8s [%(name)s] %(message)s"
LOG_FMT_FILE = "%(asctime)s %(levelname)-8s [%(name)s:%(funcName)s()] %(message)s"

LOG_DATEFMT_CONSOLE = "%m/%d/%Y %I:%M:%S %p"
LOG_DATEFMT_FILE = "%m/%d/%Y %I:%M:%S %p"

LOG_LEVEL_CONSOLE = "debug"
LOG_LEVEL_FILE = "debug"
LOG_LEVEL_HTTP = "debug"
LOG_LEVEL_AUTH = "debug"
LOG_LEVEL_API = "debug"
LOG_LEVEL_PACKAGE = "debug"

LOG_LEVELS_STR = ["debug", "info", "warning", "error", "fatal"]
LOG_LEVELS_STR_CSV = ", ".join(LOG_LEVELS_STR)
LOG_LEVELS_INT = [getattr(logging, x.upper()) for x in LOG_LEVELS_STR]
LOG_LEVELS_INT_CSV = ", ".join([format(x) for x in LOG_LEVELS_INT])

LOG_FILE_PATH = os.getcwd()
LOG_FILE_PATH_MODE = 0o700
LOG_FILE_NAME = "{pkg}.log".format(pkg=PACKAGE_ROOT)
LOG_FILE_MAX_MB = 5
LOG_FILE_MAX_FILES = 5

LOG_NAME_STDERR = "handler_stderr"
LOG_NAME_STDOUT = "handler_stdout"
LOG_NAME_FILE = "handler_file"

CSV_FIELDS = {
    "device": ["id", "serial", "mac_address", "hostname", "name"],
    "user": ["id", "username", "mail", "name"],
    "sw": ["hostname", "installed_sw_name"],
}
SETTING_UNCHANGED = ["unchanged"]
DEFAULT_NODE = "master"
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
CSV_ADAPTER = "csv"
DEBUG_MATCHES = False

DEFAULT_PERM = "ReadOnly"

VALID_PERMS = ["Restricted", "ReadWrite", "ReadOnly"]

COMPLEX = (dict, list, tuple)
""":obj:`tuple` of :obj:`type` -
A set of types that are considered as complex.
"""
EMPTY = [None, "", [], {}, ()]
""":obj:`list` of :obj:`type` -
Values that should be considered as empty.
"""
LIST = (tuple, list)
""":obj:`tuple` of :obj:`type` -
Types that are considered as lists.
"""
STR = six.string_types
""":obj:`tuple` of :obj:`type` -
Types that are considered as strings.
"""
INT = six.integer_types
""":obj:`tuple` of :obj:`type` -
Types that are considered as integers.
"""
BYTES = six.binary_type
SIMPLE = tuple(list(STR) + [int, bool, float])
""":obj:`tuple` of :obj:`type` -
Types that are considered as simple.
"""
SIMPLE_NONE = tuple(list(SIMPLE) + [None])
""":obj:`tuple` of :obj:`type` -
Types that are considered as simple or None.
"""
YES = [True, 1, "1", "true", "t", "yes", "y", "yas"]
""":obj:`list` of :obj:`type` -
Values that should be considered as truthy.
"""
NO = [False, 0, "0", "false", "f", "no", "n", "noes"]
""":obj:`list` of :obj:`type` -
Values that should be considered as falsey.
"""
PY36 = sys.version_info[0:2] >= (3, 6)
PY37 = sys.version_info[0:2] >= (3, 7)
