# -*- coding: utf-8 -*-
"""Utilities and tools."""
import calendar
import codecs
import csv
import inspect
import io
import ipaddress
import json
import logging
import pathlib
import platform
import re
import sys
import types
import typing as t
from datetime import datetime, timedelta, timezone
from itertools import zip_longest
from urllib.parse import urljoin

import click
import dateutil.parser
import dateutil.relativedelta
import dateutil.tz

from . import INIT_DOTENV, PACKAGE_FILE, PACKAGE_ROOT, VERSION
from .constants.api import GUI_PAGE_SIZES
from .constants.general import (
    DEBUG_ARGS,
    DEBUG_TMPL,
    ERROR_ARGS,
    ERROR_TMPL,
    FILE_DATE_FMT,
    NO,
    OK_ARGS,
    OK_TMPL,
    SECHO_ARGS,
    TRIM_MSG,
    URL_STARTS,
    WARN_ARGS,
    WARN_TMPL,
    YES,
)
from .constants.logs import MAX_BODY_LEN
from .exceptions import ToolsError
from .setup_env import find_dotenv, get_env_ax

LOG: logging.Logger = logging.getLogger(PACKAGE_ROOT).getChild("tools")
EMAIL_RE_STR: str = (
    r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")"
    r"@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"
)
EMAIL_RE: t.Pattern = re.compile(EMAIL_RE_STR, re.I)
PathLike: t.TypeVar = t.TypeVar("PathLike", pathlib.Path, str, bytes)
DAYS_MAP: dict = dict(zip(range(7), calendar.day_name))
CoerceIO: t.TypeVar = t.Union[str, bytes, t.IO]


def type_str(
    value: t.Any, max_len: int = 60, join: t.Optional[str] = ", "
) -> t.Union[str, t.List[str]]:
    """Pass."""
    length = len(str(value))
    svalue = f"{str(value)[:max_len]}...snip..." if length >= max_len else f"{value}"
    items = [
        f"type={type(value)}",
        f"length={length}",
        f"value={svalue!r}",
    ]
    return join.join(items) if isinstance(join, str) else items


def pathify(
    path: PathLike,
    path_strict: bool = True,
    path_encoding: str = "utf-8",
    resolve: bool = True,
    expanduser: bool = True,
    as_file: bool = False,
    as_dir: bool = False,
    exts: t.Optional[t.List[str]] = None,
) -> pathlib.Path:
    """Convert a str into a fully resolved & expanded Path object."""
    check_type(value=path, exp=(str, bytes, pathlib.Path))

    if isinstance(path, bytes):
        path = bytes_to_str(value=path, strict=path_strict, encoding=path_encoding)
        resolved = pathlib.Path(path.splitlines()[0])
    elif isinstance(path, str):
        resolved = pathlib.Path(path.splitlines()[0])
    elif isinstance(path, pathlib.Path):
        resolved = path

    if expanduser:
        resolved = resolved.expanduser()

    if resolve:
        resolved = resolved.resolve()

    vstr = f"(supplied {type_str(path)})"
    rstr = f"Resolved path {str(resolved)!r}"

    if as_file and not resolved.is_file():
        raise ToolsError(f"{rstr} does not exist as a file {vstr}")

    if as_dir and not resolved.is_dir():
        raise ToolsError(f"{rstr} does not exist as a directory {vstr}")

    if isinstance(exts, list) and exts and resolved.suffix not in exts:
        raise ToolsError(f"{rstr} with extension {resolved.suffix!r} is not one of {exts}")

    return resolved


def is_existing_file(path: t.Any, **kwargs) -> bool:
    """Check if the supplied value refers to an existing file."""
    if isinstance(path, pathlib.Path) and path.is_file():
        return True

    try:
        if isinstance(path, (str, bytes)):
            return pathify(path=path, **kwargs).is_file()
    except Exception:
        return False

    return False


def listify(obj: t.Any, dictkeys: bool = False) -> list:
    """Force an object into a list.

    Notes:
        * :obj:`list`: returns as is
        * :obj:`tuple`: convert to list
        * :obj:`None`: returns as an empty list
        * any of :data:`axonius_api_client.constants.general.SIMPLE`: return as a list of obj
        * :obj:`dict`: if dictkeys is True, return as list of keys of obj,
          otherwise return as a list of obj

    Args:
        obj: object to coerce to list
        dictkeys: if obj is dict, return list of keys of obj
    """
    if isinstance(obj, types.GeneratorType):
        return obj
    if isinstance(obj, list):
        return obj
    if obj is None:
        return []
    if isinstance(obj, (tuple, set)):
        return list(obj)
    if dictkeys and isinstance(obj, dict):
        return list(obj)
    return [obj]


def grouper(iterable: t.Iterable, n: int, fillvalue: t.Optional[t.Any] = None) -> t.Iterator:
    """Split an iterable into chunks.

    Args:
        iterable: iterable to split into chunks of size n
        n: length to split iterable into
        fillvalue: value to use as filler for last chunk
    """
    return zip_longest(*([iter(iterable)] * n), fillvalue=fillvalue)


def coerce_int(
    obj: t.Any,
    max_value: t.Optional[int] = None,
    min_value: t.Optional[int] = None,
    allow_none: bool = False,
    valid_values: t.Optional[t.List[int]] = None,
    errmsg: t.Optional[str] = None,
) -> int:
    """Convert an object into int.

    Args:
        obj: object to convert to int

    Raises:
        :exc:`ToolsError`: if obj is not able to be converted to int
    """
    if allow_none and (obj is None or str(obj).lower().strip() in ["none", "null"]):
        return None

    pre = f"{errmsg}\n" if errmsg else ""

    try:
        value = int(obj)
    except Exception:
        raise ToolsError(f"{pre}Supplied value {obj!r} of type {trype(obj)} is not an integer.")

    if max_value is not None and value > max_value:
        raise ToolsError(f"{pre}Supplied value {obj!r} is greater than max value of {max_value}.")

    if min_value is not None and value < min_value:
        raise ToolsError(f"{pre}Supplied value {obj!r} is less than min value of {min_value}.")

    if valid_values and value not in valid_values:
        raise ToolsError(f"{pre}Supplied value {obj!r} is not one of {valid_values}.")

    return value


def coerce_int_float(value: t.Union[int, float, str]) -> t.Union[int, float]:
    """Convert an object into int or float.

    Args:
        obj: object to convert to int or float

    Raises:
        :exc:`ToolsError`: if obj is not able to be converted to int or float
    """
    if isinstance(value, float):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value = value.strip()

        if value.isdigit():
            return int(value)

        if value.replace(".", "").isdigit():
            return float(value)

    vtype = trype(value)
    raise ToolsError(f"Supplied value {value!r} of type {vtype} is not an integer or float.")


def coerce_bool(obj: t.Any, errmsg: t.Optional[str] = None) -> bool:
    """Convert an object into bool.

    Args:
        obj: object to coerce to bool, will check against
            :data:`axonius_api_client.constants.general.YES` and
            :data:`axonius_api_client.constants.general.NO`

    Raises:
        :exc:`ToolsError`: obj is not able to be converted to bool
    """

    def combine(obj):
        return ", ".join([f"{x!r}" for x in obj])

    coerce_obj = obj

    if isinstance(obj, str):
        coerce_obj = coerce_obj.lower().strip()

    if coerce_obj in YES:
        return True

    if coerce_obj in NO:
        return False

    vtype = trype(obj)
    msg = listify(errmsg)
    msg += [
        f"Supplied value {coerce_obj!r} of type {vtype} must be one of:",
        f"  For True: {combine(YES)}",
        f"  For False: {combine(NO)}",
    ]
    raise ToolsError("\n".join(msg))


def is_str(value: t.Any, not_empty: bool = True) -> bool:
    """Check if value is non empty string."""
    return isinstance(value, str) and (
        isinstance(value, str) and bool(value.strip()) if not_empty else True
    )


def is_email(value: t.Any) -> bool:
    """Check if a value is a valid email."""
    return is_str(value=value, not_empty=True) and bool(EMAIL_RE.fullmatch(value))


def is_int(obj: t.Any, digit: bool = False) -> bool:
    """Check if obj is int typeable.

    Args:
        obj: object to check
        digit: allow checking str/bytes
    """
    if digit:
        if (isinstance(obj, str) or isinstance(obj, bytes)) and obj.isdigit():
            return True

    return not isinstance(obj, bool) and isinstance(obj, int)


def join_url(url: str, *parts) -> str:
    """Join a URL to any number of parts.

    Args:
        url: str to add parts to
        *parts: str(s) to append to url
    """
    url = url.rstrip("/") + "/"
    for part in parts:
        if not part:
            continue
        url = url.rstrip("/") + "/"
        part = part.lstrip("/")
        url = urljoin(url, part)
    return url


def strip_right(obj: t.Union[t.List[str], str], fix: str) -> t.Union[t.List[str], str]:
    """Strip text from the right side of obj.

    Args:
        obj: str(s) to strip fix from
        fix: str to remove from obj(s)
    """
    if isinstance(obj, list) and all([isinstance(x, str) for x in obj]):
        return [strip_right(obj=x, fix=fix) for x in obj]

    if isinstance(obj, str):
        plen = len(fix)

        if obj.endswith(fix):
            return obj[:-plen]

    return obj


def strip_left(obj: t.Union[t.List[str], str], fix: str) -> t.Union[t.List[str], str]:
    """Strip text from the left side of obj.

    Args:
        obj: str(s) to strip fix from
        fix: str to remove from obj(s)
    """
    if isinstance(obj, list) and all([isinstance(x, str) for x in obj]):
        return [strip_left(obj=x, fix=fix) for x in obj]

    if isinstance(obj, str):
        plen = len(fix)

        if obj.startswith(fix):
            return obj[plen:]

    return obj


class AxJSONEncoder(json.JSONEncoder):
    """Pass."""

    def __init__(self, *args, **kwargs):
        """Pass."""
        self.fallback = kwargs.pop("fallback", None)
        super().__init__(*args, **kwargs)

    def default(self, obj):
        """Pass."""
        if isinstance(obj, datetime):
            return obj.isoformat()

        if has_to_dict(obj):
            return obj.to_dict()

        if callable(getattr(self, "fallback", None)):
            return self.fallback(obj)

        return super().default(obj)  # pragma: no cover


def has_to_dict(obj: t.Any) -> bool:
    """Pass."""
    return hasattr(obj, "to_dict") and callable(obj.to_dict)


def json_dump(
    obj: t.Any,
    indent: int = 2,
    sort_keys: bool = False,
    error: bool = True,
    fallback: t.Any = str,
    to_dict: bool = True,
    cls: t.Type = AxJSONEncoder,
    **kwargs,
) -> t.Any:
    """Serialize an object into json str.

    Args:
        obj: object to serialize into json str
        indent: json str indent level
        sort_keys: sort dict keys
        error: if json error happens, raise it
        **kwargs: passed to :func:`json.dumps`
    """
    obj = bytes_to_str(value=obj)

    if to_dict and has_to_dict(obj):
        obj = obj.to_dict()

    try:
        return json.dumps(
            obj, indent=indent, sort_keys=sort_keys, cls=cls, fallback=fallback, **kwargs
        )
    except Exception:  # pragma: no cover
        if error:
            raise
        return obj


def lens(value: t.Any) -> t.Optional[int]:
    """Pass."""
    try:
        return len(value)
    except Exception:
        return None


def tlens(value: t.Any) -> t.Optional[int]:
    """Pass."""
    return f"type={trype(value)}, length={lens(value)}"


def json_load(
    obj: t.Union[str, t.IO, pathlib.Path], error: bool = True, close_fh: bool = True, **kwargs
) -> t.Any:
    """Deserialize a json str into an object.

    Args:
        obj: str to deserialize into obj
        error: if json error happens, raise it
        **kwargs: passed to :func:`json.loads`
    """
    load = obj
    method = json.loads
    fh = None
    if is_existing_file(load):
        method = json.load
        path = pathify(obj)
        fh = load = path.open()

    if isinstance(load, (io.TextIOBase, io.BufferedIOBase)):
        method = json.load

    try:
        return method(load, **kwargs)
    except Exception as exc:
        msgs = [
            f"Unable to load JSON from supplied {tlens(obj)}",
            f"error: {exc}",
        ]
        msgs = "\n".join(msgs)
        LOG.exception(msgs)
        if error:
            nexc = ToolsError(msgs)
            nexc.obj = obj
            nexc.load = load
            nexc.orig_exc = exc
            raise nexc

        return obj
    finally:
        try:
            if close_fh and fh is not None:
                fh.close()
        except Exception:
            pass


def is_file_like(value: t.Any) -> bool:
    """Pass."""
    return isinstance(value, (io.TextIOBase, io.BufferedIOBase))


def csv_load(
    value: t.Union[str, bytes, PathLike, t.IO],
    encoding: str = "utf-8-sig",
    restkey: t.Optional[str] = "extra_columns",
    close_fh: bool = True,
    **kwargs,
) -> csv.DictReader:
    """Pass."""
    kwargs["restkey"] = restkey
    fh = None
    if is_existing_file(value):
        path = pathify(value)
        kwargs["f"] = fh = path.open(newline="", encoding=encoding)
    elif is_file_like(value):
        fh = value
        kwargs["f"] = value
    elif isinstance(value, str):
        kwargs["f"] = io.StringIO(value)
    elif isinstance(value, bytes):
        kwargs["f"] = io.BytesIO(value)
    try:
        reader = csv.DictReader(**kwargs)
        reader.rows = list(reader)
        return reader
    except Exception as exc:
        msgs = [
            f"Unable to load CSV {tlens(value)} using args {kwargs}",
            f"error: {exc}",
        ]
        msgs = "\n".join(msgs)
        LOG.exception(msgs)

        nexc = ToolsError(msgs)
        nexc.value = value
        nexc.kwargs = kwargs
        nexc.orig_exc = exc
        raise nexc
    finally:
        if close_fh and fh is not None:
            try:
                fh.close()
            except Exception:
                pass


def jsonl_loader(item: str, idx: int, error: bool = True, **kwargs) -> t.Any:
    """Pass."""
    try:
        return json.loads(item, **kwargs)
    except Exception as exc:
        msgs = [
            f"Unable to load JSONL item #{idx + 1}: {item}",
            f"error: {exc}",
        ]
        msgs = "\n".join(msgs)
        LOG.exception(msgs)

        if error:
            nexc = ToolsError(msgs)
            nexc.item = item
            nexc.orig_exc = exc
            raise nexc


def jsonl_load(
    obj: t.Union[str, t.List[str], t.IO], error: bool = True, close_fh: bool = True, **kwargs
) -> t.List[t.Any]:
    """Deserialize a jsonl str into an object.

    Args:
        obj: str to deserialize into obj
        error: if json error happens, raise it
        **kwargs: passed to :func:`json.loads`
    """

    def is_item(item):
        if not isinstance(item, str):
            return False
        if not item.strip() or item.startswith("#"):
            return False
        return True

    fh = None

    if is_existing_file(obj):
        path = pathify(obj)
        fh = path.open()
        items = fh.readlines
    elif is_file_like(obj):
        fh = obj
        items = obj.readlines
    elif isinstance(obj, (tuple, list)):
        items = obj
    elif isinstance(obj, str):
        items = obj.splitlines
    else:
        raise ToolsError(f"Unexpected type {tlens(obj)}, must be str, bytes, {t.IO}, or {PathLike}")

    ret = [
        jsonl_loader(item=item, idx=idx, error=error, **kwargs)
        for idx, item in enumerate(items() if callable(items) else items)
        if is_item(item)
    ]
    try:
        if close_fh and fh is not None:
            fh.close()
    except Exception:
        pass
    return ret


def json_log(
    obj: t.Any,
    error: bool = False,
    trim: t.Optional[int] = MAX_BODY_LEN,
    trim_lines: bool = True,
    trim_msg: str = TRIM_MSG,
    **kwargs,
) -> str:  # pragma: no cover
    """Pass."""
    return json_reload(
        obj=obj, error=error, trim=trim, trim_lines=trim_lines, trim_msg=trim_msg, **kwargs
    )


def json_reload(
    obj: t.Any,
    error: bool = False,
    trim: t.Optional[int] = None,
    trim_lines: bool = False,
    trim_msg: str = TRIM_MSG,
    **kwargs,
) -> str:
    """Re-serialize a json str into a pretty json str.

    Args:
        obj: str to deserialize into obj and serialize back to str
        error: If json error happens, raise it
        **kwargs: passed to :func:`json_dump`
    """
    obj = json_load(obj=obj, error=error)
    if not isinstance(obj, str):
        obj = json_dump(obj=obj, error=error, **kwargs)
    obj = coerce_str(value=obj, trim=trim, trim_msg=trim_msg, trim_lines=trim_lines)
    return obj


def text_load(
    value: t.Union[str, t.List[str], t.IO], close_fh: bool = True
) -> t.Generator[str, None, None]:
    """Pass."""
    fh = None
    if is_existing_file(value):
        path = pathify(value)
        fh = path.open()
        lines = fh.readlines
    elif is_file_like(value):
        fh = value
        lines = value.readlines
    elif isinstance(value, str):
        lines = value.splitlines
    elif isinstance(value, (list, tuple)):
        lines = value
    else:
        raise ToolsError(
            f"Must supply str, list of str, {pathlib.Path}, or {t.IO}, supplied {tlens(value)}"
        )

    try:
        yield from [line for line in (lines() if callable(lines) else lines)]
    finally:
        try:
            if close_fh and fh is not None:
                fh.close()
        except Exception:
            pass


def dt_parse(obj: t.Union[str, timedelta, datetime], default_tz_utc: bool = False) -> datetime:
    """Parse a str, datetime, or timedelta into a datetime object.

    Notes:
        * :obj:`str`: will be parsed into datetime obj
        * :obj:`datetime.timedelta`: will be parsed into datetime obj as now - timedelta
        * :obj:`datetime.datetime`: will be re-parsed into datetime obj

    Args:
        obj: object or list of objects to parse into datetime
    """
    if isinstance(obj, list) and all([isinstance(x, str) for x in obj]):
        return [dt_parse(obj=x) for x in obj]

    if isinstance(obj, datetime):
        obj = str(obj)

    if isinstance(obj, timedelta):
        obj = str(dt_now() - obj)

    value = dateutil.parser.parse(obj)

    if default_tz_utc and not value.tzinfo:
        value = value.replace(tzinfo=dateutil.tz.tzutc())

    return value


def dt_parse_tmpl(obj: t.Union[str, timedelta, datetime], tmpl: str = "%Y-%m-%d") -> str:
    """Parse a string into the format used by the REST API.

    Args:
        obj: date time to parse using :meth:`dt_parse`
        tmpl: strftime template to convert obj into
    """
    valid_fmts = [
        "YYYY-MM-DD",
        "YYYYMMDD",
    ]
    try:
        dt = dt_parse(obj=obj)
        return dt.strftime(tmpl)
    except Exception:
        vtype = trype(obj)
        valid = "\n - " + "\n - ".join(valid_fmts)
        raise ToolsError(
            (
                f"Could not parse date {obj!r} of type {vtype}"
                f", try a string in the format of:{valid}"
            )
        )


def dt_now(
    delta: t.Optional[timedelta] = None,
    tz: timezone = dateutil.tz.tzutc(),
) -> datetime:
    """Get the current datetime in for a specific tz.

    Args:
        delta: convert delta into datetime str instead of returning now
        tz: timezone to return datetime in
    """
    if isinstance(delta, timedelta):
        return dt_parse(obj=delta)
    return datetime.now(tz)


def dt_now_file(fmt: str = FILE_DATE_FMT, **kwargs):
    """Pass."""
    return dt_now(**kwargs).strftime(fmt)


def dt_sec_ago(obj: t.Union[str, timedelta, datetime], exact: bool = False) -> int:
    """Get number of seconds ago a given datetime was.

    Args:
        obj: parsed by :meth:`dt_parse` into a datetime obj
    """
    obj = dt_parse(obj=obj)
    now = dt_now(tz=obj.tzinfo)
    value = (now - obj).total_seconds()
    return value if exact else round(value)


def dt_min_ago(obj: t.Union[str, timedelta, datetime]) -> int:
    """Get number of minutes ago a given datetime was.

    Args:
        obj: parsed by :meth:`dt_sec_ago` into seconds ago
    """
    return round(dt_sec_ago(obj=obj) / 60)


def dt_days_left(obj: t.Optional[t.Union[str, timedelta, datetime]]) -> t.Optional[int]:
    """Get number of days left until a given datetime.

    Args:
        obj: parsed by :meth:`dt_sec_ago` into days left
    """
    ret = None
    if obj:
        obj = dt_parse(obj=obj)
        now = dt_now(tz=obj.tzinfo)
        seconds = (obj - now).total_seconds()
        ret = round(seconds / 60 / 60 / 24)
    return ret


def dt_within_min(
    obj: t.Union[str, timedelta, datetime],
    n: t.Optional[t.Union[str, int]] = None,
) -> bool:
    """Check if given datetime is within the past n minutes.

    Args:
        obj: parsed by :meth:`dt_min_ago` into minutes ago
        n: int of :meth:`dt_min_ago` should be greater than or equal to
    """
    if not is_int(obj=n, digit=True):
        return False

    return dt_min_ago(obj=obj) >= int(n)


def get_path(obj: PathLike) -> pathlib.Path:
    """Convert a str into a fully resolved & expanded Path object.

    Args:
        obj: obj to convert into expanded and resolved absolute Path obj
    """
    return pathlib.Path(obj).expanduser().resolve()


def path_read(
    obj: PathLike, binary: bool = False, is_json: bool = False, **kwargs
) -> t.Union[bytes, str]:
    """Read data from a file.

    Notes:
        * if path filename ends with ".json", data will be deserialized using
          :meth:`json_load`

    Args:
        obj: path to read data form, parsed by :meth:`get_path`
        binary: read the data as binary instead of str
        is_json: deserialize data using :meth:`json_load`
        **kwargs: passed to :meth:`json_load`

    Raises:
        :exc:`ToolsError`: path does not exist as file
    """
    robj = get_path(obj=obj)

    if not robj.is_file():
        raise ToolsError(f"Supplied path='{obj}' (resolved='{robj}') does not exist!")

    if binary:
        data = robj.read_bytes()
    else:
        data = robj.read_text()

    if is_json:
        data = json_load(obj=data, **kwargs)

    if robj.suffix == ".json" and isinstance(data, str):
        kwargs.setdefault("error", False)
        data = json_load(obj=data, **kwargs)

    return robj, data


def get_backup_filename(path: PathLike) -> str:
    """Pass."""
    path = get_path(obj=path)
    return f"{path.stem}_{dt_now_file()}{path.suffix}"


def get_backup_path(path: PathLike) -> pathlib.Path:
    """Pass."""
    path = get_path(obj=path)
    return path.parent / get_backup_filename(path=path)


def check_path_is_not_dir(path: PathLike) -> pathlib.Path:
    """Pass."""
    path = get_path(obj=path)
    if path.is_dir():
        raise ToolsError(f"'{path}' is a directory, not a file")
    return path


def path_create_parent_dir(
    path: PathLike, make_parent: bool = True, protect_parent=0o700
) -> pathlib.Path:
    """Pass."""
    path = get_path(obj=path)

    if not path.parent.is_dir():
        if make_parent:
            path.parent.mkdir(mode=protect_parent, parents=True, exist_ok=True)
        else:
            raise ToolsError(
                f"Parent directory '{path.parent}' does not exist and make_parent is False"
            )
    return path


def path_backup_file(
    path: PathLike,
    backup_path: t.Optional[PathLike] = None,
    make_parent: bool = True,
    protect_parent=0o700,
    **kwargs,
) -> pathlib.Path:
    """Pass."""
    path = get_path(obj=path)
    if not path.is_file():
        raise ToolsError(f"'{path}' does not exist as a file, can not backup")

    if backup_path:
        backup_path = get_path(obj=backup_path)
    else:
        backup_path = get_backup_path(path=path)

    check_path_is_not_dir(path=backup_path)

    if backup_path.is_file():
        backup_path = get_backup_path(path=backup_path)

    path_create_parent_dir(path=backup_path, make_parent=make_parent, protect_parent=protect_parent)
    path.rename(backup_path)
    return backup_path


def auto_suffix(
    path: PathLike,
    data: t.Union[bytes, str],
    error: bool = False,
    **kwargs,
) -> t.Union[bytes, str]:
    """Pass."""
    path = get_path(obj=path)

    if path.suffix == ".json" and not (isinstance(data, str) or isinstance(data, bytes)):
        data = json_dump(obj=data, error=error, **kwargs)
    return data


def path_write(
    obj: PathLike,
    data: t.Union[bytes, str],
    overwrite: bool = False,
    backup: bool = False,
    backup_path: t.Optional[PathLike] = None,
    binary: bool = False,
    binary_encoding: str = "utf-8",
    is_json: bool = False,
    make_parent: bool = True,
    protect_file=0o600,
    protect_parent=0o700,
    suffix_auto: bool = True,
    **kwargs,
) -> t.Tuple[pathlib.Path, t.Tuple[int, t.Optional[pathlib.Path]]]:
    """Write data to a file.

    Notes:
        * if obj filename ends with ".json", serializes data using :meth:`json_dump`.

    Args:
        obj: path to write data to, parsed by :meth:`get_path`
        data: data to write to obj
        binary: write the data as binary instead of str
        binary_encoding: encoding to use when switching from str/bytes
        is_json: serialize data using :meth:`json_load`
        overwrite: overwrite obj if exists
        make_parent: If the parent directory does not exist, create it
        protect_file: octal mode of permissions to set on file
        protect_dir: octal mode of permissions to set on parent directory when creating
        **kwargs: passed to :meth:`json_dump`

    Raises:
        :exc:`ToolsError`: path exists as file and overwrite is False
        :exc:`ToolsError`: if parent path does not exist and make_parent is False
    """
    obj = get_path(obj=obj)

    if is_json:
        data = json_dump(**combo_dicts(kwargs, obj=data))

    if suffix_auto:
        data = auto_suffix(**combo_dicts(kwargs, path=obj, data=data))

    if binary:
        if isinstance(data, str):
            data = data.encode(binary_encoding)
        method = obj.write_bytes
    else:
        if isinstance(data, bytes):
            data = data.decode(binary_encoding)
        method = obj.write_text

    check_path_is_not_dir(path=obj)

    if obj.exists():
        if backup:
            backup_path = path_backup_file(
                path=obj,
                backup_path=backup_path,
                make_parent=make_parent,
                protect_parent=protect_parent,
            )
        elif overwrite is False:
            raise ToolsError(f"File '{obj}' already exists and overwrite is False")
    else:
        path_create_parent_dir(path=obj, make_parent=make_parent, protect_parent=protect_parent)

    obj.touch()

    if protect_file:
        obj.chmod(protect_file)

    bytes_written = method(data)
    return obj, (bytes_written, backup_path)


def longest_str(obj: t.List[str]) -> int:
    """Determine the length of the longest string in a list of strings.

    Args:
        obj: list of strings to calculate length of
    """
    return round(max([len(x) + 5 for x in obj]), -1)


def split_str(
    obj: t.Union[t.List[str], str],
    split: str = ",",
    strip: t.Optional[str] = None,
    do_strip: bool = True,
    lower: bool = True,
    empty: bool = False,
) -> t.List[str]:
    """Split a string or list of strings into a list of strings.

    Args:
        obj: string or list of strings to split
        split: character to split on
        strip: characters to strip
        do_strip: strip each item from the split
        lower: lowercase each item from the split
        empty: remove empty items post split
    """
    if obj is None:
        return []

    if isinstance(obj, list):
        return [
            y
            for x in obj
            for y in split_str(
                obj=x,
                split=split,
                strip=strip,
                do_strip=do_strip,
                lower=lower,
                empty=empty,
            )
        ]

    if not isinstance(obj, str):
        raise ToolsError(f"Unable to split non-str value {obj}")

    ret = []
    for x in obj.split(split):
        if lower:
            x = x.lower()
        if do_strip:
            x = x.strip(strip)
        if not empty and not x:
            continue
        ret.append(x)
    return ret


def echo_debug(msg: str, **kwargs):
    """Echo a message to console.

    Args:
        msg: message to echo
        kwargs: passed to ``echo``
    """
    kwargs.setdefault("style_args", DEBUG_ARGS)
    kwargs.setdefault("style_tmpl", DEBUG_TMPL)
    kwargs.setdefault("log_level", "debug")
    return echo(msg=msg, **kwargs)


def echo_ok(msg: str, **kwargs):
    """Echo a message to console.

    Args:
        msg: message to echo
        kwargs: passed to ``echo``
    """
    kwargs.setdefault("style_args", OK_ARGS)
    kwargs.setdefault("style_tmpl", OK_TMPL)
    kwargs.setdefault("log_level", "info")
    return echo(msg=msg, **kwargs)


def echo_warn(msg: str, **kwargs):
    """Echo a warning message to console.

    Args:
        msg: message to echo
        kwargs: passed to ``echo``
    """
    kwargs.setdefault("style_args", WARN_ARGS)
    kwargs.setdefault("style_tmpl", WARN_TMPL)
    kwargs.setdefault("log_level", "warning")
    kwargs["do_echo"] = True
    return echo(msg=msg, **kwargs)


def echo_error(msg: str, abort=True, **kwargs):
    """Echo an error message to console.

    Args:
        msg: message to echo
        abort: call sys.exit(1) after echoing message
        kwargs: passed to ``echo``
    """
    kwargs.setdefault("style_args", ERROR_ARGS)
    kwargs.setdefault("style_tmpl", ERROR_TMPL)
    kwargs.setdefault("log_level", "error")
    kwargs.setdefault("abort_code", 1)
    kwargs["do_echo"] = True
    return echo(msg=msg, abort=abort, **kwargs)


def echo(
    msg: t.Optional[t.Union[str, t.List[str]]] = None,
    abort: bool = False,
    tmpl: bool = True,
    log: t.Optional[logging.Logger] = None,
    log_level: str = "debug",
    log_method: t.Optional[t.Callable] = None,
    log_fallback: t.Callable = LOG.debug,
    style_tmpl: t.Optional[str] = None,
    style_args: t.Optional[dict] = None,
    joiner: str = "\n",
    do_echo: bool = True,
    abort_code: int = 0,
    **kwargs,
):
    """Pass."""
    if isinstance(msg, (list, tuple)):
        msg = joiner.join(msg)

    if callable(log_method):
        use_method = log_method
    elif isinstance(log, logging.Logger):
        use_method = getattr(log, log_level)
    else:
        use_method = log_fallback

    use_method(msg)

    if do_echo:
        echo_msg = msg

        fmt_args = {}
        fmt_args.update(locals())
        fmt_args.update(kwargs)
        if tmpl and is_str(style_tmpl):
            echo_msg = style_tmpl.format(**fmt_args)

        style_args = style_args if isinstance(style_args, dict) else {}
        echo_args = get_secho_args(kwargs=kwargs, **style_args)
        echo_args["message"] = echo_msg
        click.secho(**echo_args)

    if abort:
        sys.exit(abort_code)


def sysinfo() -> dict:
    """Gather system information."""
    try:
        cli_args = sys.argv
    except Exception:  # pragma: no cover
        cli_args = "No sys.argv!"

    info = {}
    info["API Client Version"] = VERSION
    info["API Client Package"] = PACKAGE_FILE
    info["Init loaded .env file"] = INIT_DOTENV
    info["Path to .env file"] = find_dotenv()
    info["OS envs"] = get_env_ax()
    info["Date"] = str(dt_now())
    info["Python System Version"] = ", ".join(sys.version.splitlines())
    info["Command Line Args"] = cli_args
    platform_attrs = [
        "machine",
        "node",
        "platform",
        "processor",
        "python_branch",
        "python_compiler",
        "python_implementation",
        "python_revision",
        "python_version",
        "release",
        "system",
        "version",
        "win32_edition",
    ]
    for attr in platform_attrs:
        method = getattr(platform, attr, None)
        value = "unavailable"
        if method:
            value = method()

        attr = attr.replace("_", " ").title()
        info[attr] = value
    return info


def calc_percent(part: t.Union[int, float], whole: t.Union[int, float], places: int = 2) -> float:
    """Calculate the percentage of part out of whole.

    Args:
        part: number to get percent of whole
        whole: number to caclulate against part
        places: number of decimal places to return
    """
    if 0 in [part, whole]:
        value = 0.00
    elif part > whole:
        value = 100.00
    else:
        value = 100 * (part / whole)

    value = trim_float(value=value, places=places)
    return value


def trim_float(value: float, places: int = 2) -> float:
    """Trim a float to N places.

    Args:
        value: float to trim
        places: decimal places to trim value to
    """
    if isinstance(places, int):
        value = float(f"{value:.{places}f}")
    return value


def join_kv(
    obj: t.Union[t.List[dict], dict], listjoin: str = ", ", tmpl: str = "{k}: {v!r}"
) -> t.List[str]:
    """Join a dictionary into key value strings.

    Args:
        obj: dict or list of dicts to stringify
        listjoin: string to use for joining
        tmpl: template to format key value pairs of dict
    """
    if isinstance(obj, list):
        return [join_kv(obj=x, listjoin=listjoin, tmpl=tmpl) for x in obj]

    if not isinstance(obj, dict):
        raise ToolsError(f"Object must be a dict, supplied {trype(obj)}")

    items = []
    for k, v in obj.items():
        if isinstance(v, (list, tuple)):
            v = listjoin.join([str(i) for i in v])
            items.append(tmpl.format(k=k, v=v))
            continue

        if isinstance(v, dict):
            items.append(f"{k}:")
            items += join_kv(obj=v, listjoin=listjoin, tmpl="  " + tmpl)
            continue

        items.append(tmpl.format(k=k, v=v))

    return items


def get_type_str(obj: t.Any):
    """Get the type name of a class.

    Args:
        obj: class or tuple of classes to get type name(s) of
    """
    if isinstance(obj, (list, tuple)):
        return " or ".join([x.__name__ for x in obj])
    else:
        return obj.__name__


def check_type(value: t.Any, exp: t.Any, name: str = "", exp_items: t.Optional[t.Any] = None):
    """Check that a value is the appropriate type.

    Args:
        value: value to check type of
        exp: type(s) that value should be
        name: identifier of what value is for
        exp_items: if value is a list, type(s) that list items should be
    """
    name = f" for {name!r}" if name else ""

    if not isinstance(value, exp):
        vtype = get_type_str(obj=type(value))
        etype = get_type_str(obj=exp)
        err = f"Required type {etype}{name} but received type {vtype}: {value!r}"
        raise ToolsError(err)

    if exp_items and isinstance(value, list):
        for idx, item in enumerate(value):
            if isinstance(item, exp_items):
                continue
            vtype = get_type_str(obj=type(item))
            etype = get_type_str(obj=exp_items)
            err = (
                f"Required type {etype}{name} in list item {idx} but received "
                f"type {vtype}: {value!r}"
            )
            raise ToolsError(err)


def check_empty(value: t.Any, name: str = ""):
    """Check if a value is empty.

    Args:
        value: value to check type of
        name: identifier of what value is for
    """
    if not value:
        name = f" for {name!r}" if name else ""
        err = f"Required value{name} but received an empty {trype(value)}: {value!r}"
        raise ToolsError(err)


def get_raw_version(value: str) -> str:
    """Caclulate the raw bits of a version str.

    Args:
        value: version to calculate
    """
    check_type(value=value, exp=str)
    converted = "0"
    version = value
    if ":" in value:
        if "." in value and value.index(":") > value.index("."):
            raise ToolsError(f"Invalid version with ':' after '.' in {value!r}")
        converted, version = value.split(":", 1)
    octects = version.split(".")
    for octect in octects:
        if not octect.isdigit():
            raise ToolsError(f"Invalid version with non-digit {octect!r} in {value!r}")
        if len(octect) > 8:
            octect = octect[:8]
        converted += "".join(["0" for _ in range(8 - len(octect))]) + octect
    return converted


def coerce_str_to_csv(
    value: str,
    coerce_list: bool = False,
    errmsg: t.Optional[str] = None,
) -> t.List[str]:
    """Coerce a string into a list of strings.

    Args:
        value: string to seperate using comma
    """
    pre = f"{errmsg}\n" if errmsg else ""

    new_value = value
    if isinstance(value, str):
        new_value = [x.strip() for x in value.split(",") if x.strip()]
        if not new_value:
            raise ToolsError(f"{pre}Empty value after parsing CSV: {value!r}")

    if not isinstance(new_value, (list, tuple)):
        if coerce_list:
            new_value = listify(obj=new_value)
        else:
            raise ToolsError(f"{pre}Invalid type {trype(new_value)} supplied, must be a list")

    if not new_value:
        raise ToolsError(f"{pre}Empty list supplied {value}")

    return new_value


def parse_ip_address(value: str) -> t.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
    """Parse a string into an IP address.

    Args:
        value: ip address
    """
    try:
        return ipaddress.ip_address(value)
    except Exception as exc:
        raise ToolsError(str(exc))


def parse_ip_network(value: str) -> t.Union[ipaddress.IPv4Network, ipaddress.IPv6Network]:
    """Parse a string into an IP network.

    Args:
        value: ip network
    """
    if "/" not in str(value):
        raise ToolsError(
            (
                f"Supplied value {value!r} of type {trype(value)} is not a valid subnet "
                "- format must be <address>/<CIDR>."
            )
        )
    try:
        return ipaddress.ip_network(value)
    except Exception as exc:
        raise ToolsError(str(exc))


def kv_dump(obj: dict) -> str:
    """Get a string representation of a dictionaries key value pairs.

    Args:
        obj: dictionary to get string of
    """
    return "\n  " + "\n  ".join([f"{k}: {v}" for k, v in obj.items()])


def bom_strip(content: t.Union[str, bytes], strip=True, bom: bytes = codecs.BOM_UTF8) -> str:
    """Remove the UTF-8 BOM marker from the beginning of a string.

    Args:
        content: string to remove BOM marker from if found
        strip: remove whitespace before & after removing BOM marker
    """
    content = content.strip() if strip else content

    if isinstance(bom, bytes) and isinstance(content, str):
        bom = bom.decode()
    elif isinstance(bom, str) and isinstance(content, bytes):
        bom = bom.encode()

    bom_len = len(bom)
    if content.startswith(bom):
        content = content[bom_len:]

    content = content.strip() if strip else content
    return content


def read_stream(stream) -> str:
    """Try to read input from a stream.

    Args:
        stream: stdin or a file descriptor to read input from
    """
    stream_name = format(getattr(stream, "name", stream))

    if stream.isatty():
        raise ToolsError(f"No input provided on {stream_name!r}")

    # its STDIN with input or a file
    content = stream.read().strip()

    if not content:
        raise ToolsError(f"Empty content supplied to {stream_name!r}")

    return content


def check_gui_page_size(size: t.Optional[int] = None) -> int:
    """Check page size to see if it one of the valid GUI page sizes.

    Args:
        size: page size to check

    Raises:
        :exc:`ApiError`: if size is not one of
            :data:`axonius_api_client.constants.api.GUI_PAGE_SIZES`

    """
    size = size or GUI_PAGE_SIZES[0]
    size = coerce_int(size)
    if size not in GUI_PAGE_SIZES:
        raise ToolsError(f"gui_page_size of {size} is invalid, must be one of {GUI_PAGE_SIZES}")
    return size


def calc_gb(value: t.Union[str, int], places: int = 2, is_kb: bool = True) -> float:
    """Convert bytes into GB.

    Args:
        value: bytes
        places: decimal places to trim value to
        is_kb: values are in kb or bytes
    """
    value = coerce_int_float(value=value)
    value = value / 1024 / 1024
    value = (value / 1024) if not is_kb else value
    value = trim_float(value=value, places=places)
    return value


def calc_perc_gb(
    obj: dict,
    whole_key: str,
    part_key: str,
    perc_key: t.Optional[str] = None,
    places: int = 2,
    update: bool = True,
    is_kb: bool = True,
) -> dict:
    """Calculate the GB and percent from a dict.

    Args:
        obj: dict to get whole_key and part_key from
        whole_key: key to get whole value from and convert to GB and set as whole_key_gb
        part_key: key to get part value from and convert to GB and set as part_key_gb
        perc_key: key to set percent in
        is_kb: values are in kb or bytes
    """
    perc_key = perc_key or f"{part_key}_percent"
    whole_value = obj[whole_key] or 0
    part_value = obj[part_key] or 0
    whole_gb = calc_gb(value=whole_value, places=places, is_kb=is_kb)
    part_gb = calc_gb(value=part_value, places=places, is_kb=is_kb)
    perc = calc_percent(part=part_gb, whole=whole_gb, places=places)
    ret = obj if update else {}
    ret[f"{part_key}_gb"] = part_gb
    ret[f"{whole_key}_gb"] = whole_gb
    ret[perc_key] = perc
    return ret


def get_subcls(cls: type, excludes: t.Optional[t.List[type]] = None) -> list:
    """Get all subclasses of a class."""
    excludes = excludes or []
    subs = [s for c in cls.__subclasses__() for s in get_subcls(c)]
    return [x for x in list(set(cls.__subclasses__()).union(subs)) if x not in excludes]


def prettify_obj(obj: t.Union[dict, list], indent: int = 0) -> t.List[str]:
    """Pass."""
    spaces = " " * indent
    sub_indent = indent + 2
    if isinstance(obj, dict):
        lines = ["", f"{spaces}-----"] if not indent else []
        for k, v in obj.items():
            lines += [f"{spaces}- {k}:", *prettify_obj(v, sub_indent)]
        return lines
    elif isinstance(obj, list):
        return [y for x in obj for y in prettify_obj(x, indent)]
    return [f"{spaces} {obj}"]


def token_parse(obj: str) -> str:
    """Pass."""
    url_check = "token="
    if isinstance(obj, str) and url_check in obj:
        idx = obj.index(url_check) + len(url_check)
        obj = obj[idx:]
    return obj


def combo_dicts(*args, **kwargs) -> dict:
    """Pass."""
    # TBD make this descend
    ret = {}
    for x in args:
        if isinstance(x, dict):
            ret.update(x)

    ret.update(kwargs)
    return ret


def is_url(value: str) -> bool:
    """Pass."""
    return isinstance(value, str) and any([value.startswith(x) for x in URL_STARTS])


def bytes_to_str(value: t.Any) -> t.Union[str, t.Any]:
    """Convert obj to str if it is bytes."""
    return value.decode() if isinstance(value, bytes) else value


def strip_str(value: t.Any) -> t.Union[str, t.Any]:
    """Strip a value if it is a string."""
    return value.strip() if isinstance(value, str) else value


def coerce_str(
    value: t.Any,
    strip: bool = True,
    none: t.Any = "",
    trim: t.Optional[int] = None,
    trim_lines: bool = False,
    trim_msg: str = TRIM_MSG,
) -> t.Union[str, t.Any]:
    """Coerce a value to a string."""
    value = bytes_to_str(value=value)
    if value is None:
        value = none

    if not isinstance(value, str):
        value = str(value)

    if strip:
        value = strip_str(value=value)

    value = str_trim(value=value, trim=trim, trim_lines=trim_lines, trim_msg=trim_msg)
    return value


def str_trim(
    value: str,
    trim: t.Optional[int] = None,
    trim_lines: bool = False,
    trim_msg: str = TRIM_MSG,
) -> str:
    """Pass."""
    trim_type = "lines" if trim_lines else "characters"

    if isinstance(trim, int) and trim > 0:
        trim_done = False
        if trim_lines:
            value = value.splitlines()
            value_len = len(value)
            if value_len >= trim:
                value = value[:trim]
                trim_done = True
            value = "\n".join(value)
        else:
            value_len = len(value)
            if value_len >= trim:
                value = value[:trim]
                trim_done = True

        if trim_done:
            value += trim_msg.format(trim_type=trim_type, trim=trim, value_len=value_len)
    return value


def strim(value: str, limit: t.Optional[int] = None) -> str:
    """Pass."""
    if isinstance(limit, int) and limit > 0 and len(value) > limit:
        value = value[:limit] + f"... {len(value) - limit} more characters"
    return value


def ltrim(
    value: t.Union[str, t.List[str]], limit: t.Optional[int] = None, rejoin: bool = False
) -> t.List[str]:
    """Pass."""
    if isinstance(value, str):
        value = value.splitlines()
    value = listify(value)

    if isinstance(limit, int) and limit > 0 and len(value) > limit:
        value = value[:limit] + [f"... {len(value) - limit} more lines"]
    return value


def get_cls_path(value: t.Any) -> str:
    """Pass."""
    if inspect.isclass(value):
        cls = value
    elif hasattr(value, "__class__"):
        cls = value.__class__
    else:
        cls = value

    if hasattr(cls, "__module__") and hasattr(cls, "__name__"):
        return f"{cls.__module__}.{cls.__name__}"

    return str(value)


def csv_writer(
    rows: t.List[dict],
    columns: t.Optional[t.List[str]] = None,
    quotes: str = "nonnumeric",
    dialect: str = "excel",
    line_ending: str = "\n",
    stream: t.Optional[t.IO] = None,
    key_extra_error: bool = False,
    key_missing_value: t.Optional[t.Any] = None,
) -> str:  # pragma: no cover
    """Pass."""
    quotes = getattr(csv, f"QUOTE_{quotes.upper()}")
    if not columns:
        columns = []
        for row in rows:
            columns += [x for x in row if x not in columns]

    stream = stream if is_file_like(stream) else io.StringIO()
    writer = csv.DictWriter(
        stream,
        fieldnames=columns,
        quoting=quotes,
        lineterminator=line_ending,
        dialect=dialect,
        restval=key_missing_value,
        extrasaction="raise" if key_extra_error else "ignore",
    )
    writer.writerow(dict(zip(columns, columns)))
    writer.writerows(rows)
    stream.seek(0)
    content = stream.getvalue()
    return content


def parse_int_min_max(value, default=0, min_value=None, max_value=None):
    """Pass."""
    if isinstance(value, str) and value.isdigit():
        value = int(value)

    if not isinstance(value, int):
        value = default

    if min_value is not None and value < min_value:
        value = default

    if max_value is not None and value > max_value:
        value = default

    return value


def safe_replace(obj: dict, value: str) -> str:
    """Pass."""
    for search, replace in obj.items():
        if isinstance(search, str) and isinstance(replace, str) and search and search in value:
            value = value.replace(search, replace)
    return value


def safe_format(
    value: PathLike, mapping: t.Optional[t.Dict[str, str]] = None, as_path: bool = False, **kwargs
) -> PathLike:
    """Pass."""
    is_path = isinstance(value, pathlib.Path)
    to_update = str(value) if is_path else value

    if not isinstance(to_update, str):
        return value

    for item in [mapping, kwargs]:
        if isinstance(item, dict) and item:
            to_update = safe_replace(obj=item, value=to_update)

    return get_path(to_update) if is_path or as_path else to_update


def get_paths_format(
    *args, mapping: t.Optional[t.Dict[str, str]] = None
) -> t.Optional[pathlib.Path]:
    """Pass."""
    ret = None
    for path in args:
        if isinstance(path, bytes):
            path = path.decode("utf-8")

        if isinstance(path, pathlib.Path):
            path = str(path)

        if isinstance(path, str):
            if isinstance(mapping, dict):
                path = safe_replace(obj=mapping, value=path)

            path = pathlib.Path(path)

        if isinstance(path, pathlib.Path):
            path = path.expanduser()

            if ret:
                ret = ret / path
            else:
                ret = path.resolve()
    return ret


def int_days_map(
    value: t.Union[str, t.List[t.Union[str, int]]], names: bool = False
) -> t.List[str]:
    """Pass."""
    ret = []
    value = coerce_str_to_csv(value=value, coerce_list=True)
    valid = ", ".join([f"{v} ({k})" for k, v in DAYS_MAP.items()])

    for item in value:
        found = False
        for number, name in DAYS_MAP.items():
            if isinstance(item, str) and item.lower() == name.lower():
                ret.append(number)
                found = True

            if (isinstance(item, str) and item.isdigit()) or isinstance(item, int):
                item = coerce_int(
                    obj=item,
                    min_value=0,
                    max_value=6,
                    errmsg=f"Invalid day {item!r} supplied, valid: {valid}",
                )
                if item == number:
                    ret.append(number)
                    found = True

        if not found:
            item = str(item)
            raise ToolsError(f"Invalid day {item!r} supplied, valid: {valid}")

    if names:
        ret = [v for k, v in DAYS_MAP.items() if k in ret]
    else:
        ret = [str(k) for k, v in DAYS_MAP.items() if k in ret]

    return ret


def lowish(value: t.Any) -> t.Any:
    """Pass."""
    if isinstance(value, (list, tuple)):
        return [lowish(x) for x in value]
    return value.lower() if isinstance(value, str) else value


def log_or_exc(
    msg: t.List[str],
    error: bool = True,
    log: t.Union[t.Callable, logging.Logger] = LOG,
    log_level: str = "exception",
    log_join: str = "\n",
    exc_cls: Exception = ToolsError,
    exc_args: t.Optional[dict] = None,
    **kwargs,
):
    """Pass."""
    msg = listify(msg)
    msg += listify(kwargs.get("src"))
    msg = log_join.join(msg)
    exc_args = exc_args or {}
    logmethod = getattr(log, log_level, log)
    if callable(logmethod):
        logmethod(msg)
    if error:
        raise exc_cls(msg, **exc_args)


def coerce_io(value: t.Union[str, bytes, t.IO]) -> t.IO:
    """Pass."""
    if isinstance(value, str):
        return io.StringIO(value)
    elif isinstance(value, bytes):
        return io.BytesIO(value)
    return value


def is_json_dict(value) -> bool:
    """Pass."""
    try:
        check_obj = json.loads(value) if isinstance(value, (str, bytes)) else json.load(value)
    except Exception:
        pass
    else:
        if isinstance(check_obj, dict):
            return True
    return False


def extract_kvs_auto(value: t.Union[str, bytes, t.IO], **kwargs) -> dict:
    """Pass."""
    method = extract_kvs_csv

    if callable(getattr(value, "read", None)):
        value = value.read()

    marker_json = kwargs.pop("marker_json", "json:")
    marker_semi = kwargs.pop("marker_smi", "semi:")
    marker_len = None

    if isinstance(value, (str, bytes)):
        value = value.lstrip()
        check_value = value.lower()
        if check_value.startswith(marker_json.lower()):
            marker_len = len(marker_json)
            method = extract_kvs_json
        elif check_value.startswith(marker_semi.lower()):
            marker_len = len(marker_semi)
            kwargs["delimiter"] = ";"

    if isinstance(marker_len, int):
        value = value[marker_len:]

    if is_json_dict(value):
        method = extract_kvs_json

    ret = method(value=value, **kwargs)
    return ret


def trype(value):
    """Pass."""
    return type(value).__name__


def extract_kvs_json(value: t.Union[str, bytes, t.IO], **kwargs) -> dict:
    """Pass."""
    fh = coerce_io(value)
    ret = {}
    example = {"key1": "value1", "key2": "value2"}
    example = f"Example: {json.dumps(example)!r}"

    msg = [
        f"Supplied value (type {trype(value)}): {value!r}",
        "",
        example,
        "",
    ]
    try:
        ret = json.load(fh)
    except Exception as exc:
        kwargs["msg"] = [*msg, f"ERROR: Unable to parse JSON, exception: {exc}"]
        log_or_exc(**kwargs)

    if not isinstance(ret, dict):
        kwargs["msg"] = [
            *msg,
            f"Parsed JSON contains an invalid type {trype(ret)}, must be dictionary",
            f"Parsed JSON: {ret!r}",
        ]
        log_or_exc(**kwargs)

    return ret


def is_callable(value: t.Any, attr: t.Optional[str] = None, default: t.Any = None) -> bool:
    """Pass."""
    if isinstance(attr, str):
        check = getattr(value, attr, default)
    else:
        check = value
    return callable(check)


def extract_kvs_csv(
    value: t.Union[str, bytes, t.IO] = None,
    has_headers: bool = False,
    split_kv: str = "=",
    delimiter: str = ",",
    **kwargs,
) -> dict:
    """Pass."""
    ret = {}
    fh = coerce_io(value)

    if is_callable(fh, "read") and is_callable(fh, "seek"):
        example = f"key1{split_kv}value1,key2{split_kv}value2"
        splitit = f"key/value split character {split_kv!r}"

        rows = list(csv.reader(fh, delimiter=delimiter))
        if len(rows) > 1 and split_kv not in "".join([str(x) for x in rows[0]]):
            has_headers = True

        if has_headers:
            rows = rows[1:]
        rows_cnt = len(rows)

        for row_idx, row in enumerate(rows):
            row_num = row_idx + 1
            row_info = f"row #{row_num}/{rows_cnt}"
            icnt = len(row)
            for col_idx, col in enumerate(row):
                col_num = col_idx + 1
                if not col.strip():
                    continue

                msg = [
                    f"While in {row_info} column #{col_num}/{icnt}",
                    "",
                    f"Supplied value (type {trype(value)}): {value!r}",
                    f"Row #{row_num} values: {row!r}",
                    f"Column #{col_num} value: {col}",
                    "",
                    f"Example: {example!r}",
                    "",
                ]
                if split_kv not in col:
                    kwargs["msg"] = [*msg, f"ERROR: Missing {splitit}"]
                    log_or_exc(**kwargs)
                    continue
                ikey, ivalue = col.split(split_kv, 1)
                ikey = ikey.strip()
                if not ikey.strip():
                    kwargs["msg"] = [*msg, f"ERROR: Missing/empty key before {splitit}"]
                    log_or_exc(**kwargs)
                    continue
                ret[ikey] = ivalue
    return ret


def tilde_re(value: t.Any) -> t.Optional[t.Union[str, t.Pattern]]:
    """Pass."""
    if isinstance(value, (list, tuple)):
        return [tilde_re(x) for x in value]
    if isinstance(value, str) and value.startswith("~"):
        return re.compile(value[1:], re.I)
    return value if isinstance(value, (str, t.Pattern)) else None


def is_tty(value: t.Any) -> bool:
    """Pass."""
    try:
        return value.isatty()
    except Exception:
        return False


def check_tty(value: t.Any, errmsg: str = "unable to prompt"):
    """Pass."""
    if not is_tty(value):
        raise ToolsError(f"{value!r} is not a TTY -- {errmsg}")


def check_tty_stdin():
    """Pass."""
    check_tty(sys.stdin)


def get_secho_args(kwargs: t.Optional[dict] = None, key: t.Optional[str] = None, **sargs):
    """Pass."""
    kwargs = kwargs if isinstance(kwargs, dict) else {}
    ret = {}
    skey = f"style_{key}"

    for arg in SECHO_ARGS:
        checks = [arg]

        if is_str(key):
            checks.insert(0, f"{arg}_{key}")

        for check in checks:
            if check in kwargs:
                ret.setdefault(arg, kwargs[check])
            elif check in sargs:
                ret.setdefault(arg, sargs[check])

    if skey in kwargs:
        ret.update(kwargs[skey])

    if "stderr" in ret:
        ret["err"] = ret.pop("stderr")

    ret.setdefault("err", True)
    return ret


def confirm(
    msgs: t.Optional[t.Union[str, t.List[str]]] = None,
    text: t.Optional[str] = None,
    abort: bool = False,
    default: bool = False,
    text_confirm: str = "Please confirm",
    join: str = "\n",
    check_stdin: bool = True,
    **kwargs,
):
    """Pass."""
    if check_stdin:
        check_tty_stdin()
    use_msgs = listify(msgs)
    style_msgs = kwargs.get("style_msgs", {"fg": "blue", "bold": True})
    style_text = kwargs.get("style_text", {"fg": "white", "bold": False})
    if use_msgs:
        secho_msg = get_secho_args(key="msgs", kwargs=kwargs, **style_msgs)
        click.secho(message=join.join(use_msgs), **secho_msg)
    if is_str(text):
        secho_text = get_secho_args(key="text", kwargs=kwargs, **style_text)
        click.secho(message=text, **secho_text)
    text_confirm = click.style(text_confirm, bold=True)
    answer = click.confirm(
        text=text_confirm, default=default, abort=abort, err=kwargs.get("stderr", True)
    )
    return answer


def csv_able(value: t.Optional[t.Union[str, t.List[str]]]) -> t.List[str]:
    """Pass."""
    ret = []
    if is_str(value):
        ret += [x.strip() for x in value.split(",") if is_str(x) and x not in ret]

    if isinstance(value, (list, tuple, set)):
        for item in value:
            ret += [x for x in csv_able(value=item) if x not in ret]
    return ret


def is_list(value: t.Any) -> bool:
    """Pass."""
    return isinstance(value, (list, tuple))


def style_switch(
    text: str,
    switch: bool = False,
    args_true: dict = {"fg": "green", "bold": True},
    args_false: str = {"fg": "red", "bold": True},
):
    """Pass."""
    args = args_true if switch else args_false
    return click.style(text=text, **args)


def add_source(source: str, kwargs: dict) -> str:
    """Pass."""
    ksource = kwargs.get("source", "")
    ksource = f"{ksource} / " if ksource else ""
    return f"{ksource}{source}"
