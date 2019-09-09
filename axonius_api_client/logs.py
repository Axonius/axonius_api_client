# -*- coding: utf-8 -*-
"""Axonius API Client utility tools module."""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import logging.handlers
import time

from . import __package__ as PACKAGE_ROOT
from . import constants, exceptions, tools


def gmtime():
    """Set the logging system to use GMT for time strings."""
    logging.Formatter.converter = time.gmtime


def localtime():
    """Set the logging system to use local time for time strings."""
    logging.Formatter.converter = time.localtime


def get_obj_log(obj, level=None, **kwargs):
    """Pass."""
    logger = kwargs.get("logger", logging.getLogger(obj.__class__.__module__))
    log = logger.getChild(obj.__class__.__name__)
    set_level(obj=log, level=level)
    return log


def set_level(obj, level=None):
    """Set a logger or handler to a log level.

    Args:
        obj (:obj:`logging.Logger` or :obj:`logging.Handler`):
            Object to set lvl on.
        level (:obj:`str` or :obj:`int`):
            Level to set obj to.

    """
    if level:
        obj.setLevel(getattr(logging, str_level(level=level)))


def str_level(level):
    """Get a logging level in str format.

    Args:
        level (:obj:`str` or :obj:`int`):
            Level to get str format of.

    Returns:
        :obj:`str`

    """
    if tools.is_int(obj=level, digit=True):
        level_mapped = logging.getLevelName(int(level))
        if hasattr(logging, level_mapped):
            return level_mapped

    if isinstance(level, tools.STR):
        if hasattr(logging, level.upper()):
            return level.upper()

    error = "Invalid logging level {level!r}, must be one of {lstr} or {lint}"
    error = error.format(
        level=level,
        lstr=constants.LOG_LEVELS_STR_CSV,
        lint=constants.LOG_LEVELS_INT_CSV,
    )
    raise exceptions.ToolsError(error)


def add_stderr(obj, **kwargs):
    """Add a StreamHandler to a logger object."""
    level = kwargs.get("level", constants.LOG_LEVEL_CONSOLE)
    hname = kwargs.get("hname", constants.LOG_NAME_STDERR)
    fmt = kwargs.get("fmt", constants.LOG_FMT_CONSOLE)
    datefmt = kwargs.get("datefmt", constants.LOG_DATEFMT_CONSOLE)
    htype = logging.StreamHandler

    return add_handler(
        obj=obj, hname=hname, htype=htype, level=level, fmt=fmt, datefmt=datefmt
    )


def add_stdout(obj, **kwargs):
    """Add a StreamHandler to a logger object."""
    level = kwargs.get("level", constants.LOG_LEVEL_CONSOLE)
    hname = kwargs.get("hname", constants.LOG_NAME_STDOUT)
    fmt = kwargs.get("fmt", constants.LOG_FMT_CONSOLE)
    datefmt = kwargs.get("datefmt", constants.LOG_DATEFMT_CONSOLE)
    htype = logging.StreamHandler

    return add_handler(
        obj=obj, hname=hname, htype=htype, level=level, fmt=fmt, datefmt=datefmt
    )


def add_file(obj, **kwargs):
    """Pass."""
    level = kwargs.get("level", constants.LOG_LEVEL_FILE)
    hname = kwargs.get("hname", constants.LOG_NAME_FILE)
    file_path = kwargs.get("file_path", constants.LOG_FILE_PATH)
    file_name = kwargs.get("file_name", constants.LOG_FILE_NAME)
    file_path_mode = kwargs.get("file_path_mode", constants.LOG_FILE_PATH_MODE)
    max_mb = kwargs.get("max_mb", constants.LOG_FILE_MAX_MB)
    max_files = kwargs.get("max_files", constants.LOG_FILE_MAX_FILES)
    fmt = kwargs.get("fmt", constants.LOG_FMT_FILE)
    datefmt = kwargs.get("datefmt", constants.LOG_DATEFMT_FILE)
    htype = logging.handlers.RotatingFileHandler

    path = tools.path(obj=file_path)
    path.mkdir(mode=file_path_mode, parents=True, exist_ok=True)

    handler = add_handler(
        obj=obj,
        level=level,
        htype=htype,
        fmt=fmt,
        datefmt=datefmt,
        hname=hname,
        filename=format(path / file_name),
        maxBytes=max_mb * 1024 * 1024,
        backupCount=max_files,
    )
    handler.PATH = path
    return handler


def add_null(obj, traverse=True, **kwargs):
    """Add a Null handler to a logger if it has no handlers."""
    hname = kwargs.get("hname", "NULL")
    found = find_handlers(obj=obj, hname=hname, traverse=traverse)
    htype = logging.NullHandler
    if found:
        return None
    return add_handler(obj=obj, htype=htype, hname=hname, fmt="", datefmt="", level="")


def add_handler(obj, htype, level, hname, fmt, datefmt, **kwargs):
    """Pass."""
    handler = htype(**kwargs)

    if hname:
        handler.name = hname

    if fmt:
        handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    if level:
        set_level(obj=handler, level=level)

    obj.addHandler(handler)
    return handler


def del_stderr(obj, traverse=True, **kwargs):
    """Remove a StreamHandler from a logger if found."""
    hname = kwargs.get("hname", constants.LOG_NAME_STDERR)
    htype = logging.StreamHandler
    return del_handler(obj=obj, hname=hname, htype=htype, traverse=traverse)


def del_stdout(obj, traverse=True, **kwargs):
    """Remove a StreamHandler from a logger if found."""
    hname = kwargs.get("hname", constants.LOG_NAME_STDOUT)
    htype = logging.StreamHandler
    return del_handler(obj=obj, hname=hname, htype=htype, traverse=traverse)


def del_file(obj, traverse=True, **kwargs):
    """Remove a RotatingFileHandler from a logger if found."""
    hname = kwargs.get("hname", constants.LOG_NAME_FILE)
    htype = logging.handlers.RotatingFileHandler
    return del_handler(obj=obj, hname=hname, htype=htype, traverse=traverse)


def del_null(obj, traverse=True, **kwargs):
    """Remove a Null handler from a logger if found."""
    hname = kwargs.get("hname", "NULL")
    htype = logging.NullHandler
    return del_handler(obj=obj, hname=hname, htype=htype, traverse=traverse)


def del_handler(obj, hname="", htype="", traverse=True):
    """Pass."""
    found = find_handlers(obj=obj, hname=hname, htype=htype, traverse=traverse)
    for name, handlers in found.items():
        for handler in handlers:
            logging.getLogger(name).removeHandler(handler)
    return found


def find_handlers(obj, hname="", htype=None, traverse=True):
    """Find all handlers by traversing up the tree from obj."""
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


LOG = logging.getLogger(PACKAGE_ROOT)
add_null(obj=LOG)
gmtime()
