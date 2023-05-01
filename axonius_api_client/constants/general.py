# -*- coding: utf-8 -*-
"""Constants for general use."""
import calendar
import re
import sys
import typing as t

URL_STARTS: t.List[str] = ["https://", "http://"]

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

JSON_TYPES = t.Union[int, str, float, bool, dict, list, tuple, None]

EMPTY: t.List[t.Union[str, list, dict, tuple]] = [None, "", [], {}, ()]
"""Values that should be considered as empty"""

YES_STR: t.Tuple[str, ...] = ("1", "true", "t", "yes", "y", "on")
YES: t.List[t.Union[bool, int, str]] = [True, 1, *YES_STR]
"""Values that should be considered as truthy"""

NO_STR: t.Tuple[str, ...] = ("0", "false", "f", "no", "n", "off")
NO: t.List[t.Union[bool, int, str]] = [False, 0, *NO_STR]
"""Values that should be considered as falsey"""

IS_WINDOWS: bool = sys.platform == "win32"
"""Running on a windows platform"""

IS_LINUX: bool = sys.platform == "linux"
"""Running on a linux platform"""

IS_MAC: bool = sys.platform == "darwin"
"""Running on a mac platform"""

TRIM_MSG: str = "\nTrimmed {value_len} {trim_type} down to {trim}"
FILE_DATE_FMT: str = "%Y-%m-%dT%H-%M-%S"


SECHO_ARGS: t.List[str] = [
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

EMAIL_RE_STR: str = (
    r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")"
    r"@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"
)
EMAIL_RE: t.Pattern = re.compile(EMAIL_RE_STR, re.I)
DAYS_MAP: dict = dict(zip(range(7), calendar.day_name))
HUMAN_SIZES: t.List[str] = ["bytes", "KB", "MB", "GB", "TB"]
SPLITTER: t.Pattern = re.compile(",")
HIDDEN: str = "**HIDDEN**"
ECHO: bool = False
RERAISE: bool = False

EMPTIES: t.List[t.Any] = [None, list(), set(), dict(), "", "none", "null"]
TRIM_POST: str = "... trimmed {trim_count} characters"
