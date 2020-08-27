# -*- coding: utf-8 -*-
"""Logging utilities."""
import logging
import logging.handlers
import pathlib
import sys
import time
from typing import Dict, List, Optional, Union

from . import __package__ as PACKAGE_ROOT
from .constants import (
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
from .tools import get_path, is_int


def gmtime():
    """Set the logging system to use GMT for time strings."""
    logging.Formatter.converter = time.gmtime


def localtime():
    """Set the logging system to use local time for time strings."""
    logging.Formatter.converter = time.localtime


def get_obj_log(
    obj: object, level: Optional[Union[int, str]] = None, **kwargs
) -> logging.Logger:
    """Get a child logger for an object.

    Notes:
        * level is resolved using resolved using :meth:`str_level`

    Args:
        obj (:obj:`object`): object to get a logger for
        level (:obj:`str` or :obj:`int`, optional): default ``None`` - level to set
        **kwargs:
            * logger (:obj:`logging.Logger`): default ``module of class of obj`` -
              logger to get child from

    Returns:
        :obj:`logging.Logger`: created logger child obj
    """
    logger = kwargs.get("logger", logging.getLogger(obj.__class__.__module__))
    log = logger.getChild(obj.__class__.__name__)
    set_log_level(obj=log, level=level)
    return log


def set_log_level(
    obj: Union[logging.Logger, logging.Handler], level: Optional[Union[int, str]] = None
):
    """Set a logger or handler to a log level.

    Notes:
        * level is resolved using resolved using :meth:`str_level`

    Args:
        obj (:obj:`logging.Logger` or :obj:`logging.Handler`): object to set lvl on
        level (:obj:`str` or :obj:`int`): default ``None`` - level to set
    """
    if level:
        obj.setLevel(getattr(logging, str_level(level=level)))


def str_level(level: Union[int, str]) -> str:
    """Get a logging level in str format.

    Args:
        level (:obj:`str` or :obj:`int`): level to get str format of

    Returns:
        :obj:`str`: str repr of logging level

    Raises:
        :exc:`ToolsError`: if level is not mappable as an int or str
            to known logger level in :mod:`logging`
    """
    if is_int(obj=level, digit=True):
        level_mapped = logging.getLevelName(int(level))
        if hasattr(logging, level_mapped):
            return level_mapped

    if isinstance(level, str):
        if hasattr(logging, level.upper()):
            return level.upper()

    error = (
        f"Invalid logging level {level!r}, must be one of "
        f"{LOG_LEVELS_STR_CSV} or {LOG_LEVELS_INT_CSV}"
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
        obj (:obj:`logging.Logger`): logger obj to add handler to
        **kwargs:
            * level (:obj:`logging.Logger`):
              default: :data:`axonius_api_client.LOG_LEVEL_CONSOLE` -
              log level to assign to handler
            * hname (:obj:`str`):
              default: :data:`axonius_api_client.LOG_NAME_STDERR` -
              name to assign to handler
            * fmt (:obj:`str`):
              default: :data:`axonius_api_client.LOG_FMT_CONSOLE` -
              logging format to use
            * datefmt (:obj:`str`):
              default: :data:`axonius_api_client.LOG_DATEFMT_CONSOLE` -
              date format to use

    Returns:
        :obj:`logging.StreamHandler`: handler that was added to logger obj
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
        obj (:obj:`logging.Logger`): logger obj to add handler to
        **kwargs:
            * level (:obj:`logging.Logger`):
              default: :data:`axonius_api_client.LOG_LEVEL_CONSOLE` -
              log level to assign to handler
            * hname (:obj:`str`):
              default: :data:`axonius_api_client.LOG_NAME_STDOUT` -
              name to assign to handler
            * fmt (:obj:`str`):
              default: :data:`axonius_api_client.LOG_FMT_CONSOLE` -
              logging format to use
            * datefmt (:obj:`str`):
              default: :data:`axonius_api_client.LOG_DATEFMT_CONSOLE` -
              date format to use

    Returns:
        :obj:`logging.StreamHandler`: handler that was added to logger obj
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
    file_path_mode: oct = LOG_FILE_PATH_MODE,
    max_mb: int = LOG_FILE_MAX_MB,
    max_files: int = LOG_FILE_MAX_FILES,
    fmt: str = LOG_FMT_FILE,
    datefmt: str = LOG_DATEFMT_FILE,
) -> logging.handlers.RotatingFileHandler:
    """Add a RotatingFileHandler to a logger object.

    Args:
        obj (:obj:`logging.Logger`): logger obj to add handler to
        **kwargs:
            * level (:obj:`logging.Logger`):
              default: :data:`axonius_api_client.LOG_LEVEL_FILE` -
              log level to assign to handler
            * hname (:obj:`str`):
              default: :data:`axonius_api_client.LOG_NAME_FILE` -
              name to assign to handler
            * fmt (:obj:`str`):
              default: :data:`axonius_api_client.LOG_FMT_FILE` -
              logging format to use
            * datefmt (:obj:`str`):
              default: :data:`axonius_api_client.LOG_DATEFMT_FILE` -
              date format to use
            * file_path (:obj:`str`):
              default: :data:`axonius_api_client.LOG_FILE_PATH` -
              path to write file_name to
            * file_name (:obj:`str`):
              default: :data:`axonius_api_client.LOG_FILE_NAME` -
              name of file to write log entries to
            * file_path_mode (:obj:`oct`):
              default: :data:`axonius_api_client.LOG_FILE_PATH_MODE` -
              permissions to assign to directory for log file if it has to be
              created
            * max_mb (:obj:`int`):
              default: :data:`axonius_api_client.LOG_FILE_MAX_MB` -
              rollover trigger in MB
            * max_files (:obj:`int`):
              default: :data:`axonius_api_client.LOG_FILE_MAX_FILES` -
              max files to keep for rollover

    Returns:
        :obj:`logging.StreamHandler`: handler that was added to logger obj
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
        obj (:obj:`logging.Logger`): logger obj to add handler to
        traverse (:obj:`bool`, optional): default ``True`` -

            * if ``True`` traverse the logger obj supplied up to the root logger
              to see if there are any nullhandlers attached
            * if ``False`` only check the logger obj supplied
        **kwargs:
            * hname (:obj:`str`): default: ``NULL`` - name to assign to handler

    Returns:
        :obj:`logging.NullHandler`: handler that was added to logger obj
    """
    found = find_handlers(obj=obj, hname=hname, traverse=traverse)
    if found:
        return None
    return add_handler(
        obj=obj, htype=logging.NullHandler, hname=hname, fmt="", datefmt="", level=""
    )


def add_handler(
    obj: logging.Logger,
    htype: logging.Handler,
    level: Union[str, int],
    hname: str,
    fmt: str,
    datefmt: str,
    **kwargs,
) -> logging.Handler:
    """Add a handler to a logger obj.

    Args:
        obj (:obj:`logging.Logger`): logger obj to add handler to
        htype (:class:`logging.Handler`): handler class to instantiate
        level (:obj:`str`): level to assign to handler obj
        hname (:obj:`str`): name to assign to handler obj
        fmt (:obj:`str`): logging format to assign to handler obj
        datefmt (:obj:`str`): date format to assign to handler obj
        **kwargs: passed to instantiation of htype

    Returns:
        :obj:`logging.Handler`: handler that was created and added
    """
    handler = htype(**kwargs)

    if hname:
        handler.name = hname

    if fmt:
        handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    if level:
        set_log_level(obj=handler, level=level)

    obj.addHandler(handler)
    return handler


def del_stderr(
    obj: logging.Logger, traverse: bool = True, hname: str = LOG_NAME_STDERR
) -> Dict[str, List[logging.Handler]]:
    """Remove the STDERR StreamHandler from a logger if found.

    Args:
        obj (:obj:`logging.Logger`): logger obj to remove handler from
        traverse (:obj:`bool`, optional): default ``True`` -

            * if ``True`` traverse the logger obj supplied up to the root logger
              to see if there are any attached handlers named with hname
            * if ``False`` only check the logger obj supplied for handlers named with
              hname
        **kwargs:
            * hname (:obj:`str`):
              default: :data:`axonius_api_client.LOG_NAME_FILE` -
              name of handler to search for and remove

    Returns:
        :obj:`logging.Handler`:
            dict handler handler name->[handler objects] mapping of found and
            removed handlers
    """
    return del_handler(
        obj=obj, hname=hname, htype=logging.StreamHandler, traverse=traverse
    )


def del_stdout(
    obj: logging.Logger, traverse: bool = True, hname: str = LOG_NAME_STDOUT
) -> Dict[str, List[logging.Handler]]:
    """Remove the STDOUT StreamHandler from a logger if found.

    Args:
        obj (:obj:`logging.Logger`): logger obj to remove handler from
        traverse (:obj:`bool`, optional): default ``True`` -

            * if ``True`` traverse the logger obj supplied up to the root logger
              to see if there are any attached handlers named with hname
            * if ``False`` only check the logger obj supplied for handlers named with
              hname
        **kwargs:
            * hname (:obj:`str`):
              default: :data:`axonius_api_client.LOG_NAME_STDOUT` -
              name of handler to search for and remove

    Returns:
        :obj:`logging.Handler`:
            dict handler handler name->[handler objects] mapping of found and
            removed handlers
    """
    return del_handler(
        obj=obj, hname=hname, htype=logging.StreamHandler, traverse=traverse
    )


def del_file(
    obj: logging.Logger, traverse: bool = True, hname=LOG_NAME_FILE
) -> Dict[str, List[logging.Handler]]:
    """Remove the RotatingFileHandler from a logger if found.

    Args:
        obj (:obj:`logging.Logger`): logger obj to remove handler from
        traverse (:obj:`bool`, optional): default ``True`` -

            * if ``True`` traverse the logger obj supplied up to the root logger
              to see if there are any attached handlers named with hname
            * if ``False`` only check the logger obj supplied for handlers named with
              hname
        **kwargs:
            * hname (:obj:`str`):
              default: :data:`axonius_api_client.LOG_NAME_FILE` -
              name of handler to search for and remove

    Returns:
        :obj:`logging.Handler`:
            dict handler handler name->[handler objects] mapping of found and
            removed handlers
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
        obj (:obj:`logging.Logger`): logger obj to remove handler from
        traverse (:obj:`bool`, optional): default ``True`` -

            * if ``True`` traverse the logger obj supplied up to the root logger
              to see if there are any attached handlers named with hname
            * if ``False`` only check the logger obj supplied for handlers named with
              hname
        **kwargs:
            * hname (:obj:`str`): default: NULL -
              name of handler to search for and remove

    Returns:
        :obj:`logging.Handler`:
            dict handler handler name->[handler objects] mapping of found and
            removed handlers
    """
    return del_handler(
        obj=obj, hname=hname, htype=logging.NullHandler, traverse=traverse
    )


def del_handler(
    obj: logging.Logger,
    hname: str = "",
    htype: logging.Handler = None,
    traverse: bool = True,
) -> Dict[str, List[logging.Handler]]:
    """Remove the NullHandler from a logger if found.

    Args:
        obj (:obj:`logging.Logger`): logger obj to remove handler from
        hname (:obj:`str`, optional): default ``""`` -
            name of handler to find and remove
        htype (:class:`object`, optional): default ``None`` -
            type of handler to find and remove
        traverse (:obj:`bool`, optional): default ``True`` -

            * if ``True`` traverse the logger obj supplied up to the root logger
              to see if there are any attached handlers named with hname
            * if ``False`` only check the logger obj supplied for handlers named with
              hname

    Returns:
            dict handler handler name->[handler objects] mapping of found and
            removed handlers
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
        obj (:obj:`logging.Logger`): logger obj to remove handler from
        hname (:obj:`str`, optional): default ``""`` -
            name of handler to find and remove
        htype (:class:`object`, optional): default ``None`` -
            type of handler to find and remove
        traverse (:obj:`bool`, optional): default ``True`` -

            * if ``True`` traverse the logger obj supplied up to the root logger
              to see if there are any matching attached handlers
            * if ``False`` only check the logger obj supplied for any matching
              attached handlers

    Returns:
            dict handler handler name->[handler objects] mapping of found handlers
    """
    handlers = {}

    for handler in obj.handlers:
        match_name = hname and handler.name == hname
        match_type = htype and isinstance(handler, htype)

        if match_name or match_type:
            handlers[obj.name] = handlers.get(obj.name, [])

            if handler not in handlers[obj.name]:
                handlers[obj.name].append(handler)

    if obj.parent and traverse:
        found = find_handlers(
            obj=obj.parent, hname=hname, htype=htype, traverse=traverse
        )
        handlers.update(found)

    return handlers


LOG: logging.Logger = logging.getLogger(PACKAGE_ROOT)
""":obj:`logging.Logger`: root logger used by entire package, named after package."""

add_null(obj=LOG)
gmtime()
set_log_level(obj=LOG, level=LOG_LEVEL_PACKAGE)


def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Log unhandled exceptions."""
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    LOG.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_unhandled_exception
