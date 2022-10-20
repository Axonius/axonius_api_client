# -*- coding: utf-8 -*-
"""Constants for API models."""
from typing import List

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
