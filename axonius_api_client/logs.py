# -*- coding: utf-8 -*-
"""Logging utilities."""
import logging
import logging.handlers
import pathlib
import re
import sys
import time
import typing as t
from typing import Callable, Dict, List, Optional, Tuple, Union

from . import LOG
from .constants.logs import (
    LOG_DATEFMT_CONSOLE,
    LOG_DATEFMT_FILE,
    LOG_FILE_MAX_FILES,
    LOG_FILE_MAX_MB,
    LOG_FILE_NAME,
    LOG_FILE_PATH,
    LOG_FILE_PATH_MODE,
    LOG_FMT_CONSOLE,
    LOG_FMT_FILE,
    LOG_LEVEL_CONSOLE,
    LOG_LEVEL_FILE,
    LOG_LEVEL_PACKAGE,
    LOG_LEVELS_INT_CSV,
    LOG_LEVELS_STR_CSV,
    LOG_NAME_FILE,
    LOG_NAME_STDERR,
    LOG_NAME_STDOUT,
)
from .exceptions import ToolsError
from .tools import echo_debug, echo_error, echo_ok, echo_warn, get_path, is_int

ECHOERS: Tuple[Tuple[int, Callable]] = (
    (logging.DEBUG, echo_debug),
    (logging.INFO, echo_ok),
    (logging.WARNING, echo_warn),
    (logging.ERROR, echo_error),
    (logging.CRITICAL, echo_error),
)


class HideFormatter(logging.Formatter):
    """Hide the rest of the line for any lines against :attr:`HIDE_REGEX`."""

    HIDE_ENABLED: bool = True
    """Enable hiding of matches to HIDE_REGEX."""
    HIDE_REGEX: t.Pattern = re.compile(r"(password|secret).*", re.I)
    """Pattern of sensitive info to hide."""
    HIDE_REPLACE: str = r"\1 ...REST OF LINE HIDDEN..."
    """Value to replace matches to HIDE_REGEX with."""

    def format(self, record):
        """Pass."""
        record = super().format(record)
        if self.HIDE_ENABLED:
            record = self.HIDE_REGEX.sub(self.HIDE_REPLACE, record)
        return record


def get_echoer(level: Union[int, str]) -> Callable:
    """Pass."""
    level_str = str_level(level=level)
    level_int = getattr(logging, level_str)
    for lvl_int, caller in ECHOERS:
        if lvl_int >= level_int:
            return caller
    return echo_error


def get_log_method(obj: logging.Logger, level: Optional[str] = None) -> Callable:
    """Pass."""
    level = level.lower() if isinstance(level, str) else level
    ret = getattr(obj, level, None)
    return ret if callable(ret) else lambda x: None


def gmtime():
    """Set the logging system to use GMT for time strings."""
    logging.Formatter.converter = time.gmtime
    HideFormatter.converter = time.gmtime


def localtime():
    """Set the logging system to use local time for time strings."""
    logging.Formatter.converter = time.localtime
    HideFormatter.converter = time.localtime


def get_obj_log(obj: object, level: Optional[Union[int, str]] = None, **kwargs) -> logging.Logger:
    """Get a child logger for an object.

    Args:
        obj: object to get a logger for
        level: level to set
        logger: logger to get child from
    """
    logger = kwargs.get("logger", logging.getLogger(obj.__class__.__module__))
    log = logger.getChild(obj.__class__.__name__)
    set_log_level(obj=log, level=level)
    return log


def set_log_level(
    obj: Union[logging.Logger, logging.Handler], level: Optional[Union[int, str]] = None
):
    """Set a logger or handler to a log level.

    Args:
        obj: object to set lvl on
        level: level to set
    """
    if isinstance(level, (int, str)):
        level_str = str_level(level=level)
        if level_str == "OFF":
            level_int = 0
        else:
            level_int = getattr(logging, level_str)
        obj.setLevel(level_int)


def str_level(level: Union[int, str]) -> str:
    """Get a logging level in str format.

    Args:
        level: level to get str format of

    Raises:
        :exc:`ToolsError`: if level is not mappable as an int or str to a known logger level
    """
    if is_int(obj=level, digit=True):
        level_mapped = logging.getLevelName(int(level))
        if hasattr(logging, level_mapped):
            return level_mapped

    if isinstance(level, str):
        level = level.upper()
        if hasattr(logging, level):
            return level
        if level == "OFF":
            return "OFF"

    error = (
        f"Invalid logging level {level!r}, must be one of "
        f"{LOG_LEVELS_STR_CSV} or OFF or {LOG_LEVELS_INT_CSV}"
    )
    raise ToolsError(error)


def add_stderr(
    obj: logging.Logger,
    level: Union[int, str] = LOG_LEVEL_CONSOLE,
    hname: str = LOG_NAME_STDERR,
    fmt: str = LOG_FMT_CONSOLE,
    datefmt: str = LOG_DATEFMT_CONSOLE,
) -> logging.StreamHandler:
    """Add a StreamHandler to a logger object that outputs to STDERR.

    Args:
        obj: logger obj to add handler to
        level: log level to assign to handler
        hname: name to assign to handler
        fmt: logging format to use
        datefmt: date format to use
    """
    return add_handler(
        obj=obj,
        hname=hname,
        htype=logging.StreamHandler,
        level=level,
        fmt=fmt,
        datefmt=datefmt,
    )


def add_stdout(
    obj: logging.Logger,
    level: Union[int, str] = LOG_LEVEL_CONSOLE,
    hname: str = LOG_NAME_STDOUT,
    fmt: str = LOG_FMT_CONSOLE,
    datefmt: str = LOG_DATEFMT_CONSOLE,
) -> logging.StreamHandler:
    """Add a StreamHandler to a logger object that outputs to STDOUT.

    Args:
        obj: logger obj to add handler to
        level: log level to assign to handler
        hname: name to assign to handler
        fmt: logging format to use
        datefmt: date format to use
    """
    return add_handler(
        obj=obj,
        hname=hname,
        htype=logging.StreamHandler,
        level=level,
        fmt=fmt,
        datefmt=datefmt,
    )


def add_file(
    obj: logging.Logger,
    level: Union[int, str] = LOG_LEVEL_FILE,
    hname: str = LOG_NAME_FILE,
    file_path: Union[pathlib.Path, str] = LOG_FILE_PATH,
    file_name: Union[pathlib.Path, str] = LOG_FILE_NAME,
    file_path_mode=LOG_FILE_PATH_MODE,
    max_mb: int = LOG_FILE_MAX_MB,
    max_files: int = LOG_FILE_MAX_FILES,
    fmt: str = LOG_FMT_FILE,
    datefmt: str = LOG_DATEFMT_FILE,
) -> logging.handlers.RotatingFileHandler:
    """Add a RotatingFileHandler to a logger object.

    Args:
        obj: logger obj to add handler to
        level: log level to assign to handler
        hname: name to assign to handler
        fmt: logging format to use
        datefmt: date format to use
        file_path: path to write file_name to
        file_name: name of file to write log entries to
        file_path_mode: permissions to assign to directory for log file when created
        max_mb: rollover trigger in MB
        max_files: max files to keep for rollover
    """
    path = get_path(obj=file_path)
    path.mkdir(mode=file_path_mode, parents=True, exist_ok=True)

    handler = add_handler(
        obj=obj,
        level=level,
        htype=logging.handlers.RotatingFileHandler,
        fmt=fmt,
        datefmt=datefmt,
        hname=hname,
        filename=str(path / file_name),
        maxBytes=max_mb * 1024 * 1024,
        backupCount=max_files,
    )
    handler.PATH = path
    return handler


def add_null(
    obj: logging.Logger, traverse: bool = True, hname="NULL"
) -> Optional[logging.NullHandler]:
    """Add a NullHandler to a logger if it has no handlers.

    Args:
        obj: logger obj to add handler to
        traverse: traverse the logger obj supplied up to the root logger
        hname: name to assign to handler
    """
    found = find_handlers(obj=obj, hname=hname, traverse=traverse)
    if found:
        return None
    return add_handler(obj=obj, htype=logging.NullHandler, hname=hname)


def add_handler(
    obj: logging.Logger,
    htype: logging.Handler,
    hname: str,
    fmt: str = LOG_FMT_CONSOLE,
    datefmt: str = LOG_DATEFMT_CONSOLE,
    level: Optional[Union[str, int]] = None,
    **kwargs,
) -> logging.Handler:
    """Add a handler to a logger obj.

    Args:
        obj: logger obj to add handler to
        htype: handler class to instantiate
        level: level to assign to handler obj
        hname: name to assign to handler obj
        fmt: logging format to assign to handler obj
        datefmt: date format to assign to handler obj
        **kwargs: passed to instantiation of htype
    """
    handler = htype(**kwargs)
    handler.name = hname
    set_log_level(obj=handler, level=level)
    handler.setFormatter(HideFormatter(fmt=fmt, datefmt=datefmt))
    obj.addHandler(handler)
    return handler


def del_stderr(
    obj: logging.Logger, traverse: bool = True, hname: str = LOG_NAME_STDERR
) -> Dict[str, List[logging.Handler]]:
    """Remove the STDERR StreamHandler from a logger if found.

    Args:
        obj: logger obj to remove handler from
        traverse: traverse the logger obj supplied up to the root logger
        hname: name of handler to search for and remove
    """
    return del_handler(obj=obj, hname=hname, htype=logging.StreamHandler, traverse=traverse)


def del_stdout(
    obj: logging.Logger, traverse: bool = True, hname: str = LOG_NAME_STDOUT
) -> Dict[str, List[logging.Handler]]:
    """Remove the STDOUT StreamHandler from a logger if found.

    Args:
        obj: logger obj to remove handler from
        traverse: traverse the logger obj supplied up to the root logger
        hname: name of handler to search for and remove
    """
    return del_handler(obj=obj, hname=hname, htype=logging.StreamHandler, traverse=traverse)


def del_file(
    obj: logging.Logger, traverse: bool = True, hname=LOG_NAME_FILE
) -> Dict[str, List[logging.Handler]]:
    """Remove the RotatingFileHandler from a logger if found.

    Args:
        obj: logger obj to remove handler from
        traverse: traverse the logger obj supplied up to the root logger
        hname: name of handler to search for and remove
    """
    return del_handler(
        obj=obj,
        hname=hname,
        htype=logging.handlers.RotatingFileHandler,
        traverse=traverse,
    )


def del_null(
    obj: logging.Logger, traverse: bool = True, hname: str = "NULL"
) -> Dict[str, List[logging.Handler]]:
    """Remove the NullHandler from a logger if found.

    Args:
        obj: logger obj to remove handler from
        traverse: traverse the logger obj supplied up to the root logger
        hname: name of handler to search for and remove
    """
    return del_handler(obj=obj, hname=hname, htype=logging.NullHandler, traverse=traverse)


def del_handler(
    obj: logging.Logger,
    hname: str = "",
    htype: logging.Handler = None,
    traverse: bool = True,
) -> Dict[str, List[logging.Handler]]:
    """Remove the NullHandler from a logger if found.

    Args:
        obj: logger obj to remove handler from
        traverse: traverse the logger obj supplied up to the root logger
        hname: name of handler to search for and remove
        htype: type of handler to find and remove
    """
    found = find_handlers(obj=obj, hname=hname, htype=htype, traverse=traverse)
    for name, handlers in found.items():
        for handler in handlers:
            logging.getLogger(name).removeHandler(handler)
    return found


def find_handlers(
    obj: logging.Logger,
    hname: str = "",
    htype: logging.Handler = None,
    traverse: bool = True,
) -> Dict[str, List[logging.Handler]]:
    """Remove the NullHandler from a logger if found.

    Notes:
        * will remove handler if hname supplied and handler obj name matches
        * will remove handler if htype supplied and handler obj type matches

    Args:
        obj: logger obj to search for handler in
        traverse: traverse the logger obj supplied up to the root logger
        hname: name of handler to search for
        htype: type of handler to find
    """
    handlers = {}

    for handler in obj.handlers:
        match_name = hname and handler.name == hname
        match_type = htype and isinstance(handler, htype)

        if match_name or match_type:
            handlers[obj.name] = handlers.get(obj.name, [])

            if handler not in handlers[obj.name]:  # pragma: no cover
                handlers[obj.name].append(handler)

    if obj.parent and traverse:
        found = find_handlers(obj=obj.parent, hname=hname, htype=htype, traverse=traverse)
        handlers.update(found)

    return handlers


add_null(obj=LOG)
gmtime()
set_log_level(obj=LOG, level=LOG_LEVEL_PACKAGE)


def handle_unhandled_exception(exc_type, exc_value, exc_traceback):  # pragma: no cover
    """Log unhandled exceptions."""
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    LOG.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_unhandled_exception
