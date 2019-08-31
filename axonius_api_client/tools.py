# -*- coding: utf-8 -*-
"""Axonius API Client utility tools module."""
from __future__ import absolute_import, division, print_function, unicode_literals

import csv as _csv
import datetime
import json as _json
import logging
import logging.handlers
import re
import time

import dateutil.parser
import dateutil.relativedelta
import dateutil.tz
import requests
import six

from . import __package__ as PACKAGE_ROOT
from . import api, auth, constants, exceptions, http

if six.PY2:
    import pathlib2 as pathlib  # pragma: no cover
else:
    import pathlib


def listify(obj):
    """Pass."""
    if is_type.tuple(obj):
        return list(obj)
    if is_type.none(obj):
        return []
    if is_type.simple(obj):
        return [obj]
    if is_type.dict(obj):
        return list(obj)
    return obj


def grouper(iterable, n, fillvalue=None):
    """Chunk up iterables."""
    return six.moves.zip_longest(*([iter(iterable)] * n), fillvalue=fillvalue)


def nest_depth(obj):
    """Pass."""
    if is_type.complex(obj):
        if is_type.dict(obj):
            obj = obj.values()
        calcs = [nest_depth(x) for x in obj if is_type.complex(x)]
        return 1 + (max(calcs) if calcs else 0)
    return 0


class is_type(object):
    """Pass."""

    @staticmethod
    def complex(x):
        """Pass."""
        return is_type.dict(x) or is_type.list(x)

    @staticmethod
    def bytes(obj):
        """Pass."""
        return isinstance(obj, six.binary_type)

    @staticmethod
    def str(obj):
        """Pass."""
        return isinstance(obj, six.string_types)

    @staticmethod
    def str_int(obj):
        """Pass."""
        return is_type.int(obj) or (isinstance(obj, six.string_types) and obj.isdigit())

    @staticmethod
    def int(obj):
        """Pass."""
        return not isinstance(obj, bool) and isinstance(obj, six.integer_types)

    @staticmethod
    def float(obj):
        """Pass."""
        return isinstance(obj, float)

    @staticmethod
    def dict(obj):
        """Pass."""
        return isinstance(obj, dict)

    @staticmethod
    def tuple(obj):
        """Pass."""
        return isinstance(obj, tuple)

    @staticmethod
    def list(obj):
        """Pass."""
        return isinstance(obj, (list, tuple))

    @staticmethod
    def none(obj):
        """Pass."""
        return obj is None

    @staticmethod
    def empty(obj):
        """Pass."""
        return obj in [None, "", [], {}, ()]

    @staticmethod
    def bool(obj):
        """Pass."""
        return isinstance(obj, bool)

    @staticmethod
    def simple(obj):
        """Pass."""
        return (
            is_type.str(obj)
            or is_type.int(obj)
            or is_type.bool(obj)
            or is_type.float(obj)
        )

    @staticmethod
    def lot(obj, t):
        """Pass."""
        if not is_type.list(obj):
            return False
        for x in obj:
            if not t(x):
                return False
        return True

    @staticmethod
    def los(obj):
        """Pass."""
        return is_type.lot(obj, is_type.simple)

    @staticmethod
    def lod(obj):
        """Pass."""
        return is_type.lot(obj, is_type.dict) and obj

    @staticmethod
    def lol(obj):
        """Pass."""
        return is_type.lot(obj, is_type.list) and obj

    @staticmethod
    def lols(obj):
        """Pass."""
        if not is_type.lol(obj):
            return False

        for x in obj:
            if not is_type.los(x):
                return False
        return True

    @staticmethod
    def dt(obj):
        """Pass."""
        return isinstance(obj, datetime.datetime)

    @staticmethod
    def dtdelta(obj):
        """Pass."""
        return isinstance(obj, datetime.timedelta)

    @staticmethod
    def path(obj):
        """Pass."""
        return isinstance(obj, pathlib.Path)


class path(object):
    """Pass."""

    @staticmethod
    def get(obj):
        """Pass."""
        return pathlib.Path(obj)

    @staticmethod
    def resolve(obj):
        """Pass."""
        return path.get(obj).expanduser().resolve(strict=False)

    @staticmethod
    def read(obj, binary=False, is_json=False, **kwargs):
        """Pass."""
        obj = path.resolve(obj)

        if binary:
            data = obj.read_bytes()
        else:
            data = obj.read_text()

        if is_json:
            data = json.load(data, **kwargs)

        if obj.suffix == ".json" and is_type.str(data):
            kwargs.setdefault("error", False)
            data = json.load(data, **kwargs)

        return obj, data

    @staticmethod
    def write(
        obj,
        data,
        overwrite=False,
        binary=False,
        binary_encoding="utf-8",
        is_json=False,
        make_parent=True,
        protect_file=0o600,
        protect_parent=0o700,
        **kwargs
    ):
        """Pass."""
        obj = path.resolve(obj)

        if is_json:
            data = json.dump(data, **kwargs)

        if obj.suffix == ".json" and not is_type.str(data):
            kwargs.setdefault("error", False)
            data = json.dump(data, **kwargs)

        if binary:
            if not is_type.bytes(data):
                data = data.encode(binary_encoding)
            method = obj.write_bytes
        else:
            if is_type.bytes(data):
                data = data.decode(binary_encoding)
            method = obj.write_text

        if obj.is_file() and overwrite is False:
            error = "File '{path}' already exists and overwrite is False"
            error = error.format(path=format(path))
            raise exceptions.ToolsError(error)

        if not obj.parent.is_dir():
            if make_parent:
                obj.parent.mkdir(mode=protect_parent, parents=True, exist_ok=True)
            else:
                error = "Directory '{path}' does not exist and make_parent is False"
                error = error.format(path=format(obj.parent))
                raise exceptions.ToolsError(error)

        obj.touch()

        if protect_file:
            obj.chmod(protect_file)

        return obj, method(data)


class join(object):
    """Pass."""

    @staticmethod
    def url(url, *parts):
        """Join a URL to any number of parts.

        Args:
            url (:obj:`str`):
                URL to add parts to.
            *parts: Strings to append to URL.

        Returns:
            :obj:`str`

        """
        url = url.rstrip("/") + "/"
        for part in parts:
            if not part:
                continue
            url = url.rstrip("/") + "/"
            part = part.lstrip("/")
            url = six.moves.urllib.parse.urljoin(url, part)
        return url

    @staticmethod
    def dot(obj, empty=False, joiner="."):
        """Pass."""
        obj = listify(obj)

        if not empty:
            obj = [x for x in obj if not is_type.empty(x) and format(x)]

        return joiner.join([format(x) for x in obj])

    @staticmethod
    def cr(obj, pre=True, post=False, indent="  ", joiner="\n"):
        """Pass."""
        obj = listify(obj)

        joiners = "{}{}".format(joiner, indent if indent else "")
        joined = joiners.join([format(x) for x in obj])

        if joined:
            if pre:
                joined = joiners + joined
            if post:
                joined = joined + joiners

        return joined

    @staticmethod
    def comma(obj, empty=False, indent=" ", joiner=","):
        """Pass."""
        obj = listify(obj)

        if not empty:
            obj = [x for x in obj if not is_type.empty(x) and format(x)]

        joiner = joiner + indent if indent else joiner

        return joiner.join([format(x) for x in obj])


class strip(object):
    """Pass."""

    @staticmethod
    def right(obj, postfix):
        """Pass."""
        if is_type.list(obj):
            obj = [strip.right(obj=x, postfix=postfix) for x in obj]
        elif is_type.str(obj):
            plen = len(postfix)
            obj = obj[:-plen] if obj.endswith(postfix) else obj
        return obj

    @staticmethod
    def left(obj, prefix):
        """Pass."""
        if is_type.list(obj):
            obj = [strip.left(obj=x, prefix=prefix) for x in obj]
        elif is_type.str(obj):
            plen = len(prefix)
            obj = obj[plen:] if obj.startswith(prefix) else obj
        return obj


class json(object):
    """Pass."""

    @staticmethod
    def dump(obj, indent=2, sort_keys=False, error=True, **kwargs):
        """Pass."""
        try:
            return _json.dumps(obj, indent=indent, sort_keys=sort_keys, **kwargs)
        except Exception:
            if error:
                raise
            return obj

    @staticmethod
    def load(obj, error=True, **kwargs):
        """Pass."""
        try:
            return _json.loads(obj, **kwargs)
        except Exception:
            if error:
                raise
            return obj

    @staticmethod
    def re_load(obj, error=False, **kwargs):
        """Pass."""
        obj = json.load(obj=obj, error=error)
        if not is_type.str(obj):
            obj = json.dump(obj=obj, error=error, **kwargs)
        obj = obj or ""
        if is_type.str(obj):
            obj = obj.strip()
        return obj


class dt(object):
    """Pass."""

    @staticmethod
    def parse(obj):
        """Pass."""
        if is_type.list(obj):
            return [dt.parse(x) for x in obj]

        if is_type.dt(obj):
            obj = format(obj)

        if is_type.dtdelta(obj):
            obj = format(dt.now() - obj)

        return dateutil.parser.parse(obj)

    @staticmethod
    def now(delta=None, tz=dateutil.tz.tzutc()):
        """Pass."""
        if is_type.dtdelta(delta):
            return dt.parse(delta)
        return datetime.datetime.now(tz)

    @staticmethod
    def minutes_ago(then):
        """Pass."""
        then = dt.parse(obj=then)
        now = dt.now(tz=then.tzinfo)
        return round((now - then).total_seconds() / 60)

    @staticmethod
    def within_minutes(obj, n=None):
        """Pass."""
        return False if n is None else dt.minutes_ago(obj) <= n


class csv(object):
    """Pass."""

    QUOTING = _csv.QUOTE_NONNUMERIC

    @classmethod
    def lod(
        cls,
        rows,
        stream=None,
        compress=False,
        headers=None,
        stream_value=True,
        **kwargs
    ):
        """Pass."""
        rows = cls.compress_dicts(rows) if compress else rows

        kwargs.setdefault("quoting", cls.QUOTING)
        kwargs.setdefault("f", stream or six.StringIO())
        kwargs["fieldnames"] = kwargs.get("fieldnames", headers or [])

        if not kwargs["fieldnames"]:
            for row in rows:
                for key in row:
                    if key not in kwargs["fieldnames"]:
                        kwargs["fieldnames"].append(key)

        writer = _csv.DictWriter(**kwargs)

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

        if stream_value:
            return kwargs["f"].getvalue()

        return kwargs["f"]

    @classmethod
    def _compress_complex(cls, item, pre):
        """Pass."""
        new_item = {}

        if is_type.dict(item):
            for k in list(item):
                k_pre = join.dot([pre, k])

                if is_type.simple(item[k]) or is_type.los(item[k]):
                    new_item[k_pre] = cls._crjoin(item.pop(k))
                    continue

                new_sub_item = cls._compress_complex(item[k], k_pre)
                new_item.update(new_sub_item)

                if not item[k]:
                    item.pop(k)

            return new_item

        if is_type.lod(item):
            for idx, sub_item in enumerate(list(item)):
                k_pre = join.dot([pre, idx])

                new_sub_item = cls._compress_complex(sub_item, k_pre)
                new_item.update(new_sub_item)
                if not sub_item:
                    item.remove(sub_item)
            return new_item

        if is_type.lols(item):
            new_sub_item = []

            for sub_item in list(item):
                new_sub_item.append(cls._crjoin(sub_item))
                item.remove(sub_item)

            new_item[pre] = cls._crjoin(new_sub_item)
            return new_item

        msg = "Unhandled complex type {t}: {o}"
        msg = msg.format(t=type(item), o=item)
        raise exceptions.ToolsError(msg)

    @staticmethod
    def _crjoin(obj):
        """Pass."""
        return join.cr(obj, pre=False, indent=None)

    @classmethod
    def compress_dict(cls, item):
        """Pass."""
        new_item = {}

        for k in list(item):
            if is_type.simple(item[k]) or is_type.los(item[k]):
                new_item[k] = cls._crjoin(item.pop(k))
                continue

            new_complex = cls._compress_complex(item[k], k)
            new_item.update(new_complex)

            if not item[k]:
                item.pop(k)

        return new_item

    @classmethod
    def compress_dicts(cls, items):
        """Pass."""
        return [cls.compress_dict(x) for x in items]


class logs(object):
    """Pass."""

    @staticmethod
    def gmtime():
        """Set the logging system to use GMT for time strings."""
        logging.Formatter.converter = time.gmtime

    @staticmethod
    def localtime():
        """Set the logging system to use local time for time strings."""
        logging.Formatter.converter = time.localtime

    @staticmethod
    def get_obj_log(obj, level=None, **kwargs):
        """Pass."""
        logger = kwargs.get("logger", logging.getLogger(obj.__class__.__module__))
        log = logger.getChild(obj.__class__.__name__)
        logs.set_level(obj=log, level=level)
        return log

    @staticmethod
    def set_level(obj, level=None):
        """Set a logger or handler to a log level.

        Args:
            obj (:obj:`logging.Logger` or :obj:`logging.Handler`):
                Object to set lvl on.
            level (:obj:`str` or :obj:`int`):
                Level to set obj to.

        """
        if level:
            obj.setLevel(getattr(logging, logs.str_level(level=level)))

    @staticmethod
    def str_level(level):
        """Get a logging level in str format.

        Args:
            level (:obj:`str` or :obj:`int`):
                Level to get str format of.

        Returns:
            :obj:`str`

        """
        if is_type.str(level):
            if hasattr(logging, level.upper()):
                return level.upper()
            if level.isdigit():
                level_mapped = logging.getLevelName(int(level))
                if hasattr(logging, level_mapped):
                    return level_mapped

        if is_type.int(level):
            level_mapped = logging.getLevelName(level)
            if hasattr(logging, level_mapped):
                return level_mapped

        error = "Invalid logging level {level!r}, must be one of {lstr} or {lint}"
        error = error.format(
            level=level,
            lstr=constants.LOG_LEVELS_STR_CSV,
            lint=constants.LOG_LEVELS_INT_CSV,
        )
        raise exceptions.ToolsError(error)

    @staticmethod
    def add_stderr(obj, **kwargs):
        """Add a StreamHandler to a logger object."""
        level = kwargs.get("level", constants.LOG_LEVEL_CONSOLE)
        hname = kwargs.get("hname", constants.LOG_NAME_STDERR)
        fmt = kwargs.get("fmt", constants.LOG_FMT_CONSOLE)
        datefmt = kwargs.get("datefmt", constants.LOG_DATEFMT_CONSOLE)
        htype = logging.StreamHandler

        return logs.add_handler(
            obj=obj, hname=hname, htype=htype, level=level, fmt=fmt, datefmt=datefmt
        )

    @staticmethod
    def add_stdout(obj, **kwargs):
        """Add a StreamHandler to a logger object."""
        level = kwargs.get("level", constants.LOG_LEVEL_CONSOLE)
        hname = kwargs.get("hname", constants.LOG_NAME_STDOUT)
        fmt = kwargs.get("fmt", constants.LOG_FMT_CONSOLE)
        datefmt = kwargs.get("datefmt", constants.LOG_DATEFMT_CONSOLE)
        htype = logging.StreamHandler

        return logs.add_handler(
            obj=obj, hname=hname, htype=htype, level=level, fmt=fmt, datefmt=datefmt
        )

    @staticmethod
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

        path = pathlib.Path(file_path)
        path.mkdir(mode=file_path_mode, parents=True, exist_ok=True)

        handler = logs.add_handler(
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

    @staticmethod
    def add_null(obj, traverse=True, **kwargs):
        """Add a Null handler to a logger if it has no handlers."""
        hname = kwargs.get("hname", "NULL")
        found = logs.find_handlers(obj=obj, hname=hname, traverse=traverse)
        htype = logging.NullHandler
        if found:
            return None
        return logs.add_handler(
            obj=obj, htype=htype, hname=hname, fmt="", datefmt="", level=""
        )

    @staticmethod
    def add_handler(obj, htype, level, hname, fmt, datefmt, **kwargs):
        """Pass."""
        handler = htype(**kwargs)

        if hname:
            handler.name = hname

        if fmt:
            handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

        if level:
            logs.set_level(obj=handler, level=level)

        obj.addHandler(handler)
        return handler

    @staticmethod
    def del_stderr(obj, traverse=True, **kwargs):
        """Remove a StreamHandler from a logger if found."""
        hname = kwargs.get("hname", constants.LOG_NAME_STDERR)
        htype = logging.StreamHandler
        return logs.del_handler(obj=obj, hname=hname, htype=htype, traverse=traverse)

    @staticmethod
    def del_stdout(obj, traverse=True, **kwargs):
        """Remove a StreamHandler from a logger if found."""
        hname = kwargs.get("hname", constants.LOG_NAME_STDOUT)
        htype = logging.StreamHandler
        return logs.del_handler(obj=obj, hname=hname, htype=htype, traverse=traverse)

    @staticmethod
    def del_file(obj, traverse=True, **kwargs):
        """Remove a RotatingFileHandler from a logger if found."""
        hname = kwargs.get("hname", constants.LOG_NAME_FILE)
        htype = logging.handlers.RotatingFileHandler
        return logs.del_handler(obj=obj, hname=hname, htype=htype, traverse=traverse)

    @staticmethod
    def del_null(obj, traverse=True, **kwargs):
        """Remove a Null handler from a logger if found."""
        hname = kwargs.get("hname", "NULL")
        htype = logging.NullHandler
        return logs.del_handler(obj=obj, hname=hname, htype=htype, traverse=traverse)

    @staticmethod
    def del_handler(obj, hname="", htype="", traverse=True):
        """Pass."""
        found = logs.find_handlers(obj=obj, hname=hname, htype=htype, traverse=traverse)
        for name, handlers in found.items():
            for handler in handlers:
                logging.getLogger(name).removeHandler(handler)
        return found

    @staticmethod
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
            found = logs.find_handlers(
                obj=obj.parent, hname=hname, htype=htype, traverse=traverse
            )
            handlers.update(found)

        return handlers


class Connect(object):
    """Pass.

    Attributes:
        actions (:obj:`api.actions.Actions`): Actions API object.
        adapters (TYPE): Description
        devices (TYPE): Description
        enforcements (TYPE): Description
        users (TYPE): Description

    """

    _REASON_RES = [
        re.compile(r".*?object at.*?\>\: ([a-zA-Z0-9\]\[: ]+)"),
        re.compile(r".*?\] (.*) "),
    ]

    @classmethod
    def _get_exc_reason(cls, exc):
        """Pass."""
        reason = format(exc)
        for reason_re in cls._REASON_RES:
            if reason_re.search(reason):
                return reason_re.sub(r"\1", reason).rstrip("')")
        return reason

    def __init__(self, url, key, secret, **kwargs):
        """Pass."""
        self._started = False
        self._start_dt = None
        self._wraperror = kwargs.get("wraperror", True)

        proxy = kwargs.get("proxy", "")
        certpath = kwargs.get("certpath", "")
        certverify = kwargs.get("certverify", False)
        certwarn = kwargs.get("certwarn", True)
        save_history = kwargs.get("save_history", False)
        log_request_attrs = kwargs.get("log_request_attrs", False)
        log_response_attrs = kwargs.get("log_response_attrs", False)
        log_request_body = kwargs.get("log_request_body", False)
        log_response_body = kwargs.get("log_response_body", False)
        log_logger = kwargs.get("log_logger", LOG)
        log_level_package = kwargs.get("log_level_package", constants.LOG_LEVEL_PACKAGE)
        log_level_http = kwargs.get("log_level_http", constants.LOG_LEVEL_HTTP)
        log_level_auth = kwargs.get("log_level_auth", constants.LOG_LEVEL_AUTH)
        log_level_api = kwargs.get("log_level_api", constants.LOG_LEVEL_API)
        log_level_console = kwargs.get("log_level_console", constants.LOG_LEVEL_CONSOLE)
        log_level_file = kwargs.get("log_level_file", constants.LOG_LEVEL_FILE)
        log_console = kwargs.get("log_console", False)
        log_console_method = kwargs.get("log_console_method", logs.add_stderr)
        log_file = kwargs.get("log_file", False)
        log_file_method = kwargs.get("log_file_method", logs.add_file)
        log_file_name = kwargs.get("log_file_name", constants.LOG_FILE_NAME)
        log_file_path = kwargs.get("log_file_path", constants.LOG_FILE_PATH)
        log_file_max_mb = kwargs.get("log_file_max_mb", constants.LOG_FILE_MAX_MB)
        log_file_max_files = kwargs.get(
            "log_file_max_files", constants.LOG_FILE_MAX_FILES
        )

        logs.set_level(obj=log_logger, level=log_level_package)

        self._handler_file = None
        self._handler_con = None

        if log_console:
            self._handler_con = log_console_method(
                obj=log_logger, level=log_level_console
            )

        if log_file:
            self._handler_file = log_file_method(
                obj=log_logger,
                level=log_level_file,
                file_path=log_file_path,
                file_name=log_file_name,
                max_mb=log_file_max_mb,
                max_files=log_file_max_files,
            )

        self._http_args = {
            "url": url,
            "https_proxy": proxy,
            "certpath": certpath,
            "certwarn": certwarn,
            "certverify": certverify,
            "log_level": log_level_http,
            "log_request_attrs": log_request_attrs,
            "log_response_attrs": log_response_attrs,
            "log_request_body": log_request_body,
            "log_response_body": log_response_body,
            "save_history": save_history,
        }

        self._auth_args = {"key": key, "secret": secret, "log_level": log_level_auth}

        self._http = http.Http(**self._http_args)

        self._auth = auth.ApiKey(http=self._http, **self._auth_args)

        self._api_args = {"auth": self._auth, "log_level": log_level_api}

    def start(self):
        """Pass."""
        if not self._started:
            try:
                self._auth.login()
            except Exception as exc:
                if not self._wraperror:
                    raise

                msg_pre = "Unable to connect to {url!r}".format(url=self._http.url)

                if isinstance(exc, requests.exceptions.ConnectTimeout):
                    msg = "{pre}: connection timed out after {t} seconds"
                    msg = msg.format(pre=msg_pre, t=self._http._CONNECT_TIMEOUT)
                    raise exceptions.ConnectError(msg=msg, exc=exc)
                elif isinstance(exc, requests.exceptions.ConnectionError):
                    msg = "{pre}: {reason}"
                    msg = msg.format(pre=msg_pre, reason=self._get_exc_reason(exc=exc))
                    raise exceptions.ConnectError(msg=msg, exc=exc)
                elif isinstance(exc, exceptions.InvalidCredentials):
                    msg = "{pre}: Invalid Credentials supplied"
                    msg = msg.format(pre=msg_pre, url=self._http.url)
                    raise exceptions.ConnectError(msg=msg, exc=exc)

                msg = "{pre}: {exc}"
                msg = msg.format(pre=msg_pre, exc=exc)
                raise exceptions.ConnectError(msg=msg, exc=exc)

            # TODO move these into attrs
            self.users = api.Users(**self._api_args)
            self.devices = api.Devices(**self._api_args)
            self.adapters = api.Adapters(**self._api_args)
            # self.enforcements = api.Enforcements(**self._api_args)
            # self.actions = api.Actions(**self._api_args)

            self._started = True
            self._start_dt = datetime.datetime.utcnow()

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        client = getattr(self, "_http", "")
        url = getattr(client, "url", self._http_args["url"])
        if self._started:
            uptime = datetime.datetime.utcnow() - self._start_dt
            uptime = format(uptime).split(".")[0]
            return "Connected to {url!r} for {uptime}".format(uptime=uptime, url=url)
        else:
            return "Not connected to {url!r}".format(url=url)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()


LOG = logging.getLogger(PACKAGE_ROOT)
logs.add_null(obj=LOG)
logs.gmtime()
