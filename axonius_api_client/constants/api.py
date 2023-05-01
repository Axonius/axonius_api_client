# -*- coding: utf-8 -*-
"""Constants for API models."""
from typing import List

from .general import ECHO

USE_CA_PATH: str = " > ".join(
    ["Settings", "Certificate Settings", "SSL Trust & CA Settings", "Use custom CA certificate"]
)

SETTING_UNCHANGED: List[str] = ["unchanged"]
"""used by REST API when supplying a password field that is the same in the database"""

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

MAX_PAGE_SIZE: int = 2000
"""maximum page size that REST API allows"""

PAGE_SIZE: int = MAX_PAGE_SIZE
"""API wide default page size to use."""

PAGE_SLEEP: int = 0
"""API wide default number of seconds to sleep between in page."""

GUI_PAGE_SIZES: List[int] = [20, 50, 100]
"""valid page sizes for GUI page sizes for saved queries"""

TIMEOUT_CONNECT: int = 5
"""seconds to wait for connection to API."""

TIMEOUT_RESPONSE: int = 900
"""seconds to wait for response from API."""

DEFAULT_CALLBACKS_CLS: str = "base"
"""Default callback object to use"""

COUNT_POLLING_ATTEMPTS: int = 1800
"""Number of attempts count will retry."""

COUNT_POLLING_SLEEP: int = 1
"""Number of seconds sleep will wait between attempts."""

AS_DATACLASS: bool = False
"""Global default for returning objects as dataclass instead of dict."""

BARRIER: str = "-" * 15
ASSET_TMPL: str = "{k}: {v}"
# ALL_ID: str = "all"
REFRESH: bool = 60
RE_PREFIX: str = "~"

TASK_SLOW_WARNING = """

Notice:
  Fetching a page of tasks as "basic models" is fast, but fetching each task
  individually to get the "full models" is quite slow.
  Use as many filters as possible to minimize the number of "full models" that must be fetched.

"""


class FolderDefaults:
    """Pass."""

    all_objects: bool = False
    confirm: bool = False
    delete_subfolders: bool = False
    delete_objects: bool = False
    create: bool = False
    create_action: bool = True
    echo: bool = ECHO
    echo_action: bool = True
    error_no_matches: bool = True
    error_no_objects: bool = True
    error_unmatched: bool = True
    full_objects: bool = False
    full_objects_search: bool = True
    ignore_case: bool = True
    include_details: bool = False
    include_objects: bool = False
    include_subfolders: bool = False
    copy_prefix: str = "Copy of"
    pattern_prefix: str = RE_PREFIX
    prompt: bool = False
    prompt_default: bool = False
    prompt_shell: bool = True
    query_type: str = "devices"
    recursive: bool = False
    refresh: int = REFRESH
    refresh_action: bool = True
    sep: str = "/"
