# -*- coding: utf-8 -*-
"""Axonius API Client logging tools module."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import logging.handlers
import time

import six as six

from .. import exceptions, constants

if six.PY2:
    import pathlib2 as pathlib  # pragma: no cover
else:
    import pathlib


def log_gmtime():
    """Set the logging system to use GMT for time strings."""
    logging.Formatter.converter = time.gmtime


def log_localtime():
    """Set the logging system to use local time for time strings."""
    logging.Formatter.converter = time.localtime


def log_level_set(obj, level):
    """Set a logger or handler to a log level.

    Args:
        obj (:obj:`logging.Logger` or :obj:`logging.Handler`):
            Object to set lvl on.
        level (:obj:`str` or :obj:`int`):
            Level to set obj to.

    """
    if level:
        obj.setLevel(getattr(logging, log_level_str(level=level)))


def log_level_str(level):
    """Get a logging level in str format.

    Args:
        level (:obj:`str` or :obj:`int`):
            Level to get str format of.

    Returns:
        :obj:`str`

    """
    if isinstance(level, six.string_types):
        if hasattr(logging, level.upper()):
            return level.upper()
        if level.isdigit():
            level_mapped = logging.getLevelName(int(level))
            if hasattr(logging, level_mapped):
                return level_mapped

    if isinstance(level, int):
        level_mapped = logging.getLevelName(level)
        if hasattr(logging, level_mapped):
            return level_mapped

    error = "Invalid logging level {level!r}, must be one of {lstr} or {lint}"
    error = error.format(
        level=level, lstr=constants.LEVELS_STR_CSV, lint=constants.LEVELS_INT_CSV
    )
    raise exceptions.ToolsError(error)


def add_stderr(
    obj, level="debug", hname=constants.LOG_NAME_STDERR, fmt=constants.LOG_FMT
):
    """Add a StreamHandler to a logger object."""
    return add_handler(
        obj=obj, hname=hname, htype=logging.StreamHandler, level=level, fmt=fmt
    )


def add_stdout(
    obj, level="debug", hname=constants.LOG_NAME_STDOUT, fmt=constants.LOG_FMT
):
    """Add a StreamHandler to a logger object."""
    return add_handler(
        obj=obj, hname=hname, htype=logging.StreamHandler, level=level, fmt=fmt
    )


def add_file(
    obj,
    level="debug",
    hname=constants.LOG_NAME_FILE,
    file_path=constants.LOG_FILE_PATH,
    file_name=constants.LOG_FILE_NAME,
    file_path_mode=constants.LOG_FILE_PATH_MODE,
    max_mb=constants.LOG_FILE_MAX_MB,
    max_files=constants.LOG_FILE_MAX_FILES,
    fmt=constants.LOG_FMT,
):
    """Pass."""
    path = pathlib.Path(file_path)
    path.mkdir(mode=file_path_mode, parents=True, exist_ok=True)

    return add_handler(
        obj=obj,
        htype=logging.handlers.RotatingFileHandler,
        fmt=fmt,
        hname=hname,
        filename=format(path / file_name),
        maxBytes=max_mb * 1024 * 1024,
        backupCount=max_files,
    )


def add_null(obj, hname="", traverse=True):
    """Add a Null handler to a logger if it has no handlers."""
    found = find_handlers(obj=obj, hname=hname, traverse=traverse)
    if not found:
        return add_handler(
            obj=obj, htype=logging.NullHandler, hname=hname, fmt="", level=""
        )


def add_handler(obj, htype, level="debug", hname="", fmt=constants.LOG_FMT, **kwargs):
    """Pass."""
    handler = htype(**kwargs)

    if hname:
        handler.name = hname

    if fmt:
        handler.setFormatter(logging.Formatter(fmt))

    if level:
        log_level_set(obj=handler, level=level)

    obj.addHandler(handler)
    return handler


def del_stderr(obj, hname=constants.LOG_NAME_STDOUT, traverse=True):
    """Remove a StreamHandler from a logger if found."""
    return del_handler(
        obj=obj, name=hname, htype=logging.StreamHandler, traverse=traverse
    )


def del_stdout(obj, hname=constants.LOG_NAME_STDOUT, traverse=True):
    """Remove a StreamHandler from a logger if found."""
    # return del_by_postfix(obj=obj, postfix=POSTFIX_STDOUT, traverse=traverse)
    return del_handler(
        obj=obj, name=hname, htype=logging.StreamHandler, traverse=traverse
    )


def del_file(
    obj,
    name=constants.LOG_NAME_FILE,
    htype=logging.handlers.RotatingFileHandler,
    traverse=True,
):
    """Remove a RotatingFileHandler from a logger if found."""
    return del_handler(obj=obj, name=name, htype=type, traverse=traverse)


def del_null(obj, hname="", traverse=True):
    """Remove a Null handler from a logger if found."""
    return del_handler(
        obj=obj, name=hname, htype=logging.NullHandler, traverse=traverse
    )


def del_handler(obj, hname="", htype="", traverse=True):
    """Pass."""
    found = find_handlers(obj=obj, hname=hname, htype=htype, traverse=traverse)
    for name, handlers in found.items:
        for handler in handlers:
            logging.getLogger(name).removeHandler(handler)
    return found


def find_handlers(obj, hname="", htype=None, traverse=True):
    """Find all handlers by traversing up the tree from obj."""
    handlers = {}

    for handler in obj.handlers:
        if hname and handler.name != hname:
            continue

        if htype and not isinstance(handler, htype):
            continue

        handlers[obj.name] = handlers.get(obj.name, [])

        if handler not in handlers[obj.name]:
            handlers[obj.name].append(handler)

    if obj.parent and traverse:
        handlers.update(
            find_handlers(obj=obj.parent, hname=hname, htype=htype, traverse=traverse)
        )

    return handlers
