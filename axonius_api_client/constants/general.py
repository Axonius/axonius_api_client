# -*- coding: utf-8 -*-
"""Constants for general use."""
import sys
from typing import List, Optional, Pattern, Tuple, Type, Union

URL_STARTS: List[str] = ["https://", "http://"]

OK_ARGS: dict = {"fg": "green", "bold": True, "err": True}
"""default arguments for echo_ok"""

OK_TMPL: str = "** {msg}"
"""default template for echo_ok"""

DEBUG_ARGS: dict = {"fg": "blue", "bold": False, "err": True}
"""default arguments for echo_debug"""

DEBUG_TMPL: str = "** {msg}"
"""default template for echo_debug"""

WARN_ARGS: dict = {"fg": "yellow", "bold": True, "err": True}
"""default arguments for echo_warn"""

WARN_TMPL: str = "** WARNING: {msg}"
"""default template for echo_warn"""

ERROR_ARGS: dict = {"fg": "red", "bold": True, "err": True}
"""default arguments for echo_error"""

ERROR_TMPL: str = "** ERROR: {msg}"
"""default template for echo_error"""

PY36: bool = sys.version_info[0:2] >= (3, 6)
"""python version is 3.6 or higher"""

PY37: bool = sys.version_info[0:2] >= (3, 7)
"""python version is 3.7 or higher"""

COMPLEX: Tuple[Type] = (dict, list, tuple)
"""types that are considered as complex."""

SIMPLE: Tuple[Type] = (str, int, bool, float)
"""types that are considered as simple"""

OPT_LIST_STR = Optional[Union[str, List[str]]]
STR_RE = Union[str, Pattern]
STR_RE_LISTY = Union[STR_RE, List[STR_RE]]
OPT_STR_RE_LISTY = Optional[STR_RE_LISTY]

JSON_TYPES = Union[int, str, float, bool, dict, list, tuple, None]

EMPTY: List[Union[str, list, dict, tuple]] = [None, "", [], {}, ()]
"""Values that should be considered as empty"""

YES: List[Union[bool, int, str]] = [True, 1, "1", "true", "t", "yes", "y", "on"]
"""Values that should be considered as truthy"""

NO: List[Union[bool, int, str]] = [False, 0, "0", "false", "f", "no", "n", "off"]
"""Values that should be considered as falsey"""

IS_WINDOWS: bool = sys.platform == "win32"
"""Running on a windows platform"""

IS_LINUX: bool = sys.platform == "linux"
"""Running on a linux platform"""

IS_MAC: bool = sys.platform == "darwin"
"""Running on a mac platform"""

TRIM_MSG: str = "\nTrimmed {value_len} {trim_type} down to {trim}"
FILE_DATE_FMT: str = "%Y-%m-%dT%H-%M-%S"


SECHO_ARGS: List[str] = [
    "fg",
    "bg",
    "bold",
    "dim",
    "underline",
    "overline",
    "italic",
    "blink",
    "reverse",
    "strikethrough",
    "stderr",
]
