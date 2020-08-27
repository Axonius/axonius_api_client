# -*- coding: utf-8 -*-
"""Utilities and tools."""
import ipaddress
import json
import logging
import pathlib
import platform
import sys
from datetime import datetime, timedelta, timezone
from itertools import zip_longest
from typing import Any, Callable, Iterable, Iterator, List, Optional, Tuple, Union
from urllib.parse import urljoin

import click
import dateutil.parser
import dateutil.relativedelta
import dateutil.tz

from . import __file__ as PACKAGE_FILE
from . import __package__ as PACKAGE_ROOT
from .constants import (
    ERROR_ARGS,
    ERROR_TMPL,
    NO,
    OK_ARGS,
    OK_TMPL,
    SIMPLE,
    WARN_ARGS,
    WARN_TMPL,
    YES,
)
from .exceptions import ToolsError
from .version import VERSION

LOG: logging.Logger = logging.getLogger(PACKAGE_ROOT).getChild("tools")


def listify(obj: Any, dictkeys: bool = False) -> list:
    """Force an object into a list.

    Notes:
        * :obj:`list`: returns as is
        * :obj:`tuple`: convert to list
        * :obj:`None`: returns as an empty list
        * any of :data:`axonius_api_client.SIMPLE`: return as a list of obj
        * :obj:`dict`: if dictkeys is True, return as list of keys of obj,
          otherwise return as a list of obj

    Args:
        obj (:obj:`object`): object to coerce to list
        dictkeys (:obj:`bool`, optional): default ``False`` -

            * if ``True`` and obj is dict, return list of keys of obj
            * if ``False`` and obj is dict, return list of obj

    Returns:
        :obj:`list`: coerced list
    """
    if isinstance(obj, list):
        return obj

    if isinstance(obj, tuple):
        return list(obj)

    if obj is None:
        return []

    if isinstance(obj, SIMPLE):
        return [obj]

    if isinstance(obj, dict):
        if dictkeys:
            return list(obj)

        return [obj]

    return obj


def grouper(iterable: Iterable, n: int, fillvalue: Optional[Any] = None) -> Iterator:
    """Split an iterable into chunks.

    Args:
        iterable (:obj:`typing.Iterable`): iterable to split into chunks of size n
        n (:obj:`int`): length to split iterable into
        fillvalue (:obj:`object`, optional): default ``None`` - value to use
            as filler for last chunk

    Returns:
        :obj:`typing.Iterator`: an iterator with chunks of length n
    """
    return zip_longest(*([iter(iterable)] * n), fillvalue=fillvalue)


def coerce_int(obj: Any) -> int:
    """Convert an object into int.

    Args:
        obj (:obj:`object`): object to convert to int

    Returns:
        :obj:`int`: coerced int

    Raises:
        :exc:`ToolsError`: if obj is not able to be converted to int
    """
    try:
        return int(obj)
    except Exception:
        vtype = type(obj).__name__
        raise ToolsError(f"Supplied value {obj!r} of type {vtype} is not an integer.")


def coerce_bool(obj: Any, errmsg: Optional[str] = None) -> bool:
    """Convert an object into bool.

    Notes:
        * if obj is str, will check against :data:`axonius_api_client.YES`
          and :data:`axonius_api_client.NO`

    Args:
        obj (:obj:`object`): object to coerce to bool

    Returns:
        :obj:`bool`: coerced bool

    Raises:
        :exc:`ToolsError`: obj is not able to be converted to bool
    """
    coerce_obj = obj

    if isinstance(obj, str):
        coerce_obj = coerce_obj.lower().strip()

    if coerce_obj in YES:
        return True

    if coerce_obj in NO:
        return False

    vtype = type(obj).__name__
    msg = listify(errmsg)
    msg += [
        f"Supplied value {coerce_obj!r} of type {vtype} must be one of:",
        f"  For true: {YES}",
        f"  For false: {NO}",
    ]
    raise ToolsError("\n".join(msg))


def is_int(obj: Any, digit: bool = False) -> bool:
    """Check if obj is int typeable.

    Args:
        obj (:obj:`object`): object to check
        digit (:obj:`bool`, optional): default ``False`` -
            * if ``True`` obj must be (str/bytes where isdigit is True) or int
            * if ``False`` obj must be int

    Returns:
        :obj:`bool`: bool reflecting if obj is int typeable
    """
    if digit:
        if (isinstance(obj, str) or isinstance(obj, bytes)) and obj.isdigit():
            return True

    return not isinstance(obj, bool) and isinstance(obj, int)


def join_url(url: str, *parts) -> str:
    """Join a URL to any number of parts.

    Args:
        url (:obj:`str`): str to add parts to
        *parts (:obj:`str`): str(s) to append to url

    Returns:
        :obj:`str`: url with parts appended
    """
    url = url.rstrip("/") + "/"
    for part in parts:
        if not part:
            continue
        url = url.rstrip("/") + "/"
        part = part.lstrip("/")
        url = urljoin(url, part)
    return url


def strip_right(obj: Union[List[str], str], fix: str) -> Union[List[str], str]:
    """Strip text from the right side of obj.

    Args:
        obj (:obj:`str`) or (:obj:`list` of :obj:`str`): str(s) to strip fix from
        fix (:obj:`str`): str to remove from obj(s)

    Returns:
        (:obj:`str`) or (:obj:`list` of :obj:`str`): obj with fix stripped
    """
    if isinstance(obj, list) and all([isinstance(x, str) for x in obj]):
        return [strip_right(obj=x, fix=fix) for x in obj]

    if isinstance(obj, str):
        plen = len(fix)

        if obj.endswith(fix):
            return obj[:-plen]

    return obj


def strip_left(obj: Union[List[str], str], fix: str) -> Union[List[str], str]:
    """Strip text from the left side of obj.

    Args:
        obj (:obj:`str`) or (:obj:`list` of :obj:`str`): str(s) to strip fix from
        fix (:obj:`str`): str to remove from obj(s)

    Returns:
        (:obj:`str`) or (:obj:`list` of :obj:`str`): obj with fix stripped
    """
    if isinstance(obj, list) and all([isinstance(x, str) for x in obj]):
        return [strip_left(obj=x, fix=fix) for x in obj]

    if isinstance(obj, str):
        plen = len(fix)

        if obj.startswith(fix):
            return obj[plen:]

    return obj


def json_dump(
    obj: Any, indent: int = 2, sort_keys: bool = False, error: bool = True, **kwargs
) -> str:
    """Serialize an object into json str.

    Args:
        obj (:obj:`object`): object to serialize into json str
        indent (:obj:`int`, optional): default ``2`` - json str indentation
        sort_keys (:obj:`bool`, optional): default ``False`` -

            * if ``True`` sort keys of dicts
            * if ``False`` leave keys of dicts sorted as is
        error (:obj:`bool`, optional): default ``True`` -

            * if ``True`` If json error happens, raise it
            * if ``False`` If json error happens, return original obj as is
        **kwargs: passed to :func:`json.dumps`

    Returns:
        (:obj:`str`) or (:obj:`object`):
            * object: if json error happens and error is false
            * str: if no json error happens
    """
    if isinstance(obj, bytes):
        obj = obj.decode("utf-8")

    try:
        return json.dumps(obj, indent=indent, sort_keys=sort_keys, **kwargs)
    except Exception:
        if error:
            raise
        return obj


def json_load(obj: str, error: bool = True, **kwargs) -> Any:
    """Deserialize a json str into an object.

    Args:
        obj (:obj:`object`): str to deserialize into obj
        error (:obj:`bool`, optional): default ``True`` -

            * if ``True`` If json error happens, raise it
            * if ``False`` If json error happens, return original obj as is
        **kwargs: passed to :func:`json.loads`

    Returns:
        :obj:`object`: json str serialized into python obj
    """
    try:
        return json.loads(obj, **kwargs)
    except Exception:
        if error:
            raise
        return obj


def json_reload(obj: Any, error: bool = False, trim: int = None, **kwargs) -> str:
    """Re-serialize a json str into a pretty json str.

    Args:
        obj (:obj:`object`): str to deserialize into obj and serialize back to str
        error (:obj:`bool`, optional): default ``False`` -

            * if ``True`` If json error happens, raise it
            * if ``False`` If json error happens, return original obj as is
        **kwargs: passed to :func:`json_dump`

    Returns:
        (:obj:`str`) or (:obj:`object`):
            * object: if json error happens and error is false
            * str: if no json error happens
    """
    obj = json_load(obj=obj, error=error)
    if not isinstance(obj, str):
        obj = json_dump(obj=obj, error=error, **kwargs)
    obj = obj or ""
    if isinstance(obj, str):
        obj = obj.strip()
        if trim and len(obj) >= trim:
            obj = obj[:trim] + f"\nTrimmed over {trim} characters"
    return obj


def dt_parse(obj: Union[str, timedelta, datetime]) -> datetime:
    """Parse a str, datetime, or timedelta into a datetime object.

    Notes:
        * :obj:`str`: will be parsed into datetime obj
        * :obj:`datetime.timedelta`: will be parsed into datetime obj as now - timedelta
        * :obj:`datetime.datetime`: will be re-parsed into datetime obj

    Args:
        obj (:obj:`str` or :obj:`datetime.datetime` or :obj:`datetime.timedelta`):
            object or list of objects to parse

    Returns:
        :obj:`datetime.datetime`: parsed datetime
    """
    if isinstance(obj, list) and all([isinstance(x, str) for x in obj]):
        return [dt_parse(obj=x) for x in obj]

    if isinstance(obj, datetime):
        obj = str(obj)

    if isinstance(obj, timedelta):
        obj = str(dt_now() - obj)

    return dateutil.parser.parse(obj)


def dt_parse_tmpl(obj: Union[str, timedelta, datetime], tmpl: str = "%Y-%m-%d") -> str:
    valid_fmts = [
        "YYYY-MM-DD",
        "YYYYMMDD",
    ]
    try:
        dt = dt_parse(obj=obj)
        return dt.strftime(tmpl)
    except Exception:
        vtype = type(obj).__name__
        valid = "\n - " + "\n - ".join(valid_fmts)
        raise ToolsError(
            (
                f"Could not parse date {obj!r} of type {vtype}"
                f", try a string in the format of:{valid}"
            )
        )


def dt_now(
    delta: Optional[timedelta] = None, tz: timezone = dateutil.tz.tzutc(),
) -> datetime:
    """Get the current datetime in for a specific tz.

    Args:
        delta (:obj:`datetime.timedelta`, optional): default ``None`` -
            subtract timedelta from now
        tz (:obj:`datetime.timezone`, optional): default :obj:`dateutil.tz.tzutc`:
            get now for a specific timezone

    Returns:
        :obj:`datetime.datetime`: datetime of now
    """
    if isinstance(delta, timedelta):
        return dt_parse(obj=delta)
    return datetime.now(tz)


def dt_sec_ago(obj: Union[str, timedelta, datetime], exact: bool = False) -> int:
    """Get number of seconds ago a given datetime was.

    Args:
        obj (:obj:`object`): will be parsed by :meth:`dt_parse` into a datetime obj

    Returns:
        :obj:`int`:
            int of secs ago obj was
    """
    obj = dt_parse(obj=obj)
    now = dt_now(tz=obj.tzinfo)
    value = (now - obj).total_seconds()
    return value if exact else round(value)


def dt_min_ago(obj: Union[str, timedelta, datetime]) -> int:
    """Get number of minutes ago a given datetime was.

    Args:
        obj (:obj:`object`): will be parsed by :meth:`dt_sec_ago` into seconds ago

    Returns:
        :obj:`int`: int of minutes ago obj was
    """
    return round(dt_sec_ago(obj=obj) / 60)


def dt_within_min(
    obj: Union[str, timedelta, datetime], n: Optional[Union[str, int]] = None,
) -> bool:
    """Check if given datetime is within the past n minutes.

    Args:
        obj (:obj:`object`): will be parsed by :meth:`dt_min_ago` into minutes ago
        n (:obj:`int` or :obj:`str`, optional): default ``None`` - int of
            dt_min_ago(obj) should be greater than or equal to

    Returns:
        :obj:`bool`: bool representing if obj is within the past n minutes
    """
    if not is_int(obj=n, digit=True):
        return False

    return dt_min_ago(obj=obj) >= int(n)


def get_path(obj: Union[str, pathlib.Path]) -> pathlib.Path:
    """Convert a str into a fully resolved & expanded Path object.

    Args:
        obj (:obj:`str` or :obj:`pathlib.Path`): obj to convert into
            expanded and resolved absolute Path obj

    Returns:
        :obj:`pathlib.Path`: resolved path
    """
    return pathlib.Path(obj).expanduser().resolve()


def path_read(
    obj: Union[str, pathlib.Path], binary: bool = False, is_json: bool = False, **kwargs
) -> Union[bytes, str]:
    """Read data from a file.

    Notes:
        * obj will be parsed by :meth:`path`
        * if path filename ends with ".json", data will be deserialized using
          :meth:`json_load`

    Args:
        obj (:obj:`str` or :obj:`pathlib.Path`): path to read data form
        binary (:obj:`bool`, optional): default ``False`` -

            * if ``True`` read the data as binary
            * if ``False`` read the data as str
        is_json (:obj:`bool`, optional): default ``False`` -
            * if ``True`` deserialize data using :meth:`json_load`
            * if ``False`` do not deserialize data
        **kwargs: passed to :meth:`json_load`

    Returns:
        :obj:`tuple` of (:obj:`pathlib.Path`, :obj:`object`):
            resolved path and data read from path

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


def path_write(
    obj: Union[str, pathlib.Path],
    data: Union[bytes, str],
    overwrite: bool = False,
    binary: bool = False,
    binary_encoding: str = "utf-8",
    is_json: bool = False,
    make_parent: bool = True,
    protect_file: oct = 0o600,
    protect_parent: oct = 0o700,
    # fmt: off
    **kwargs
    # fmt: on
) -> Tuple[pathlib.Path, Callable]:
    """Write data to a file.

    Notes:
        * obj will be parsed by :meth:`path`
        * if obj filename ends with ".json", serializes data using :meth:`json_dump`.

    Args:
        obj (:obj:`str` or :obj:`pathlib.Path`): path to write data to
        data (:obj:`str` or :obj:`bytes` or :obj:`object`): data to write to obj
        overwrite (:obj:`bool`, optional): default ``False`` -

            * if ``True`` overwrite obj
            * if ``False`` do not overwrite obj, raise exception if it already exists
        binary (:obj:`bool`, optional): default ``False`` -

            * if ``True`` write the data as binary
            * if ``False`` write the data as str
        binary_encoding (:obj:`str`, optional): default ``"utf-8"`` - encoding to
            use when switching from str/bytes
        is_json (:obj:`bool`, optional): default ``False`` -

            * if ``True`` Serialize data using :meth:`json_load` before writing
            * if ``False`` Do not serialize data before writing
        make_parent (:obj:`bool`, optional): default ``True`` -

            * if ``True`` If the parent directory does not exist, create it
            * if ``False`` If the parent directory does not exist, raise exception
        protect_file (:obj:`oct`): default ``0o600`` (read/write to owner only) -
            octal mode of permissions to set on file
        protect_dir (:obj:`oct`): default ``0o700`` (read/write/execute to owner only) -
            octal mode of permissions to set on parent directory when creating
        **kwargs: passed to :meth:`json_dump`

    Returns:
        :obj:`tuple` of (:obj:`pathlib.Path`, method):
            tuple of (resolved path obj, method used to write data to file)

    Raises:
        :exc:`ToolsError`: path exists as file and overwrite is False
        :exc:`ToolsError`: if parent path does not exist and make_parent
            is False
    """
    obj = get_path(obj=obj)

    if is_json:
        data = json_dump(obj=data, **kwargs)

    if obj.suffix == ".json" and not (isinstance(data, str) or isinstance(data, bytes)):
        kwargs.setdefault("error", False)
        data = json_dump(obj=data, **kwargs)

    if binary:
        if isinstance(data, str):
            data = data.encode(binary_encoding)
        method = obj.write_bytes
    else:
        if isinstance(data, bytes):
            data = data.decode(binary_encoding)
        method = obj.write_text

    if obj.is_file() and overwrite is False:
        raise ToolsError(f"File '{obj}' already exists and overwrite is False")

    if not obj.parent.is_dir():
        if make_parent:
            obj.parent.mkdir(mode=protect_parent, parents=True, exist_ok=True)
        else:
            error = f"Directory '{obj.parent}' does not exist and make_parent is False"
            raise ToolsError(error)

    obj.touch()

    if protect_file:
        obj.chmod(protect_file)

    return obj, method(data)


def longest_str(obj: List[str]) -> int:
    """Badwolf."""
    return round(max([len(x) + 5 for x in obj]), -1)


def split_str(
    obj: Union[List[str], str],
    split: str = ",",
    strip: Optional[str] = None,
    do_strip: bool = True,
    lower: bool = True,
    empty: bool = False,
) -> List[str]:
    """Split a string or list of strings into a list of strings."""
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


def echo_ok(msg: str, tmpl: bool = True, **kwargs):
    """Pass."""
    echoargs = {}
    echoargs.update(OK_ARGS)
    echoargs.update(kwargs)
    if tmpl:
        msg = OK_TMPL.format(msg=msg)

    LOG.info(msg)
    click.secho(msg, **echoargs)


def echo_warn(msg: str, tmpl: bool = True, **kwargs):
    """Pass."""
    echoargs = {}
    echoargs.update(WARN_ARGS)
    echoargs.update(kwargs)
    if tmpl:
        msg = WARN_TMPL.format(msg=msg)

    LOG.warning(msg)
    click.secho(msg, **echoargs)


def echo_error(msg: str, abort: bool = True, tmpl: bool = True, **kwargs):
    """Pass."""
    echoargs = {}
    echoargs.update(ERROR_ARGS)
    echoargs.update(kwargs)
    if tmpl:
        msg = ERROR_TMPL.format(msg=msg)

    LOG.error(msg)
    click.secho(msg, **echoargs)
    if abort:
        sys.exit(1)


def sysinfo() -> dict:
    """Pass."""
    info = {}
    info["API Client Version"] = VERSION
    info["API Client Package"] = PACKAGE_FILE
    info["Date"] = str(dt_now())
    info["Python System Version"] = ", ".join(sys.version.splitlines())
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
        try:
            method = getattr(platform, attr)
            value = method()
        except Exception:
            value = "unavailable"

        attr = attr.replace("_", " ").title()
        info[attr] = value
    return info


def calc_percent(part: Union[int, float], whole: Union[int, float]) -> float:
    """Pass."""
    if 0 in [part, whole]:
        value = 0.00
    elif part > whole:
        value = 100.00
    else:
        value = 100 * (part / whole)
    return value


def join_kv(
    obj: Union[List[dict], dict], listjoin: str = ", ", tmpl: str = "{k}: {v!r}"
) -> List[str]:
    """Pass."""
    if isinstance(obj, list):
        return [join_kv(obj=x, listjoin=listjoin, tmpl=tmpl) for x in obj]

    if not isinstance(obj, dict):
        raise ToolsError(f"Object must be a dict, supplied {type(obj)}")

    items = []
    for k, v in obj.items():
        if isinstance(v, list):
            v = listjoin.join([str(i) for i in v])
        items.append(tmpl.format(k=k, v=v))
    return items


def get_type_str(obj):
    if isinstance(obj, tuple):
        return " or ".join([x.__name__ for x in obj])
    else:
        return obj.__name__


def check_type(value, exp, name="", exp_items=None):
    """Pass."""
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


def check_empty(value, name=""):
    """Pass."""
    if not value:
        vtype = type(value).__name__
        name = f" for {name!r}" if name else ""
        err = f"Required value{name} but received an empty {vtype}: {value!r}"
        raise ToolsError(err)


def get_raw_version(value):
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


def coerce_str_to_csv(value):
    new_value = value
    if isinstance(value, str):
        new_value = [x.strip() for x in value.split(",") if x.strip()]
        if not new_value:
            raise ToolsError(f"Empty value after parsing CSV: {value!r}")

    if not isinstance(new_value, (list, tuple)):
        vtype = type(new_value).__name__
        raise ToolsError(f"Invalid type {vtype} supplied, must be a list")

    if not new_value:
        raise ToolsError(f"Empty list supplied {value}")

    return new_value


def parse_ip_address(value: str) -> Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
    try:
        return ipaddress.ip_address(value)
    except Exception as exc:
        raise ToolsError(str(exc))


def parse_ip_network(value: str) -> Union[ipaddress.IPv4Network, ipaddress.IPv6Network]:
    if "/" not in str(value):
        vtype = type(value).__name__
        raise ToolsError(
            (
                f"Supplied value {value!r} of type {vtype} is not a valid subnet "
                "- format must be <address>/<CIDR>."
            )
        )
    try:
        return ipaddress.ip_network(value)
    except Exception as exc:
        raise ToolsError(str(exc))
