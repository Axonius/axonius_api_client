# -*- coding: utf-8 -*-
"""Constants for logging."""
import logging
import os
import typing as t

from .. import DEFAULT_PATH, PACKAGE_ROOT
from ..setup_env import DEBUG

LOG_FMT_VERBOSE: str = (
    "%(asctime)s %(levelname)-8s [%(name)s:%(module)s:%(funcName)s:%(pathname)s:%(lineno)d] "
    "%(message)s"
)
"""Logging format to use for verbose logging."""

LOG_FMT_BRIEF_SRC: str = "%(levelname)-8s [%(name)s in %(module)s] %(message)s"
"""Logging format to use for brief logging."""

LOG_FMT_BRIEF: str = "%(levelname)-8s [%(name)s] %(message)s"
"""Logging format to use for brief logging."""

LOG_FMT_CONSOLE: str = LOG_FMT_VERBOSE if DEBUG else LOG_FMT_BRIEF
"""default logging format for console logs, will be verbose if package wide debugging is enabled"""

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

LOG_LEVEL_WIZARD: str = "debug"
"""default logging level for :obj:`axonius_api_client.api.wizards.wizard.Wizard`"""

LOG_LEVEL_PACKAGE: str = "debug"
"""default logging level for the entire package"""

LOG_LEVEL_ENDPOINTS_ENV: t.Optional[str] = os.environ.get("AX_ENDPOINT_LOG_LEVEL")

LOG_LEVEL_ENDPOINTS: str = (
    LOG_LEVEL_ENDPOINTS_ENV.strip()
    if (isinstance(LOG_LEVEL_ENDPOINTS_ENV, str) and LOG_LEVEL_ENDPOINTS_ENV.strip())
    else "info"
)

LOG_LEVEL_PARSE: str = "debug"

LOG_LEVELS_STR: t.List[str] = ["debug", "info", "warning", "error", "fatal"]
"""list of valid logging level strs"""

LOG_LEVELS_STR_CSV: str = ", ".join(LOG_LEVELS_STR)
"""csv of valid logging level strs"""

LOG_LEVELS_INT: t.List[int] = [getattr(logging, x.upper()) for x in LOG_LEVELS_STR]
"""list of valid logging level ints"""

LOG_LEVELS_INT_CSV: str = ", ".join([str(x) for x in LOG_LEVELS_INT])
"""csv of valid logging level ints"""

LOG_FILE_PATH: str = DEFAULT_PATH
"""default path for log files"""

LOG_FILE_PATH_MODE = 0o700
""":obj:`oct` default permissions to use when creating directories"""

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

MAX_BODY_LEN: int = 100
"""maximum body length to trim when printing request/response bodies"""

RESPONSE_ATTR_MAP: dict = {
    "url": "{url!r}",
    "size": "{body_size}",
    "method": "{method!r}",
    "status": "{status_code!r}",
    "reason": "{reason!r}",
    "elapsed": "{elapsed}",
    "headers": "{headers}",
    "cookies": "{cookies}",
}
"""Mapping of response attributes to log to their formatting strings."""

REQUEST_ATTR_MAP: dict = {
    "url": "{url!r}",
    "size": "{body_size}",
    "method": "{method!r}",
    "headers": "{headers}",
    "cookies": "{cookies}",
}
"""Mapping of request attributes to log to their formatting strings."""

RESPONSE_ATTRS: t.List[str] = list(RESPONSE_ATTR_MAP) + ["all"]
"""List of valid response attributes to log."""

REQUEST_ATTRS: t.List[str] = list(REQUEST_ATTR_MAP) + ["all"]
"""List of valid request attributes to log."""

RESPONSE_ATTRS_DEFAULT: t.Tuple[str, ...] = ("url", "status", "reason", "elapsed")
"""Default response attributes to log."""

REQUEST_ATTRS_DEFAULT: t.Tuple[str, ...] = ("url", "size")
"""Default request attributes to log."""
