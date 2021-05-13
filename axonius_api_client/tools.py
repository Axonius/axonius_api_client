# -*- coding: utf-8 -*-
"""Utilities and tools."""
import codecs
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

from . import INIT_DOTENV, PACKAGE_FILE, PACKAGE_ROOT, VERSION
from .constants.api import GUI_PAGE_SIZES
from .constants.general import (
    ERROR_ARGS,
    ERROR_TMPL,
    NO,
    OK_ARGS,
    OK_TMPL,
    WARN_ARGS,
    WARN_TMPL,
    YES,
)
from .exceptions import ToolsError
from .setup_env import find_dotenv, get_env_ax

LOG: logging.Logger = logging.getLogger(PACKAGE_ROOT).getChild("tools")


def listify(obj: Any, dictkeys: bool = False) -> list:
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
    if isinstance(obj, list):
        return obj

    if isinstance(obj, tuple):
        return list(obj)

    if obj is None:
        return []

    if isinstance(obj, dict) and dictkeys:
        return list(obj)

    return [obj]


def grouper(iterable: Iterable, n: int, fillvalue: Optional[Any] = None) -> Iterator:
    """Split an iterable into chunks.

    Args:
        iterable: iterable to split into chunks of size n
        n: length to split iterable into
        fillvalue: value to use as filler for last chunk
    """
    return zip_longest(*([iter(iterable)] * n), fillvalue=fillvalue)


def coerce_int(obj: Any, max_value: Optional[int] = None, min_value: Optional[int] = None) -> int:
    """Convert an object into int.

    Args:
        obj: object to convert to int

    Raises:
        :exc:`ToolsError`: if obj is not able to be converted to int
    """
    try:
        value = int(obj)
    except Exception:
        vtype = type(obj).__name__
        raise ToolsError(f"Supplied value {obj!r} of type {vtype} is not an integer.")

    if max_value is not None and value > max_value:
        raise ToolsError(f"Supplied value {obj!r} is greater than max value of {max_value}.")

    if min_value is not None and value < min_value:
        raise ToolsError(f"Supplied value {obj!r} is less than min value of {min_value}.")

    return value


def coerce_int_float(value: Union[int, float, str]) -> Union[int, float]:
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

    vtype = type(value).__name__
    raise ToolsError(f"Supplied value {value!r} of type {vtype} is not an integer or float.")


def coerce_bool(obj: Any, errmsg: Optional[str] = None) -> bool:
    """Convert an object into bool.

    Args:
        obj: object to coerce to bool, will check against
            :data:`axonius_api_client.constants.general.YES` and
            :data:`axonius_api_client.constants.general.NO`

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


def strip_right(obj: Union[List[str], str], fix: str) -> Union[List[str], str]:
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


def strip_left(obj: Union[List[str], str], fix: str) -> Union[List[str], str]:
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

    def default(self, obj):
        """Pass."""
        if isinstance(obj, datetime):
            return obj.isoformat()

        return super().default(obj)


def json_dump(
    obj: Any, indent: int = 2, sort_keys: bool = False, error: bool = True, **kwargs
) -> Any:
    """Serialize an object into json str.

    Args:
        obj: object to serialize into json str
        indent: json str indent level
        sort_keys: sort dict keys
        error: if json error happens, raise it
        **kwargs: passed to :func:`json.dumps`
    """
    if isinstance(obj, bytes):
        obj = obj.decode("utf-8")

    kwargs.setdefault("cls", AxJSONEncoder)
    kwargs.setdefault("default", str)

    try:
        return json.dumps(obj, indent=indent, sort_keys=sort_keys, **kwargs)
    except Exception:
        if error:
            raise
        return obj


def json_load(obj: str, error: bool = True, **kwargs) -> Any:
    """Deserialize a json str into an object.

    Args:
        obj: str to deserialize into obj
        error: if json error happens, raise it
        **kwargs: passed to :func:`json.loads`
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
        obj: str to deserialize into obj and serialize back to str
        error: If json error happens, raise it
        **kwargs: passed to :func:`json_dump`
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


def dt_parse(obj: Union[str, timedelta, datetime], default_tz_utc: bool = False) -> datetime:
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


def dt_parse_tmpl(obj: Union[str, timedelta, datetime], tmpl: str = "%Y-%m-%d") -> str:
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
        vtype = type(obj).__name__
        valid = "\n - " + "\n - ".join(valid_fmts)
        raise ToolsError(
            (
                f"Could not parse date {obj!r} of type {vtype}"
                f", try a string in the format of:{valid}"
            )
        )


def dt_now(
    delta: Optional[timedelta] = None,
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


def dt_sec_ago(obj: Union[str, timedelta, datetime], exact: bool = False) -> int:
    """Get number of seconds ago a given datetime was.

    Args:
        obj: parsed by :meth:`dt_parse` into a datetime obj
    """
    obj = dt_parse(obj=obj)
    now = dt_now(tz=obj.tzinfo)
    value = (now - obj).total_seconds()
    return value if exact else round(value)


def dt_min_ago(obj: Union[str, timedelta, datetime]) -> int:
    """Get number of minutes ago a given datetime was.

    Args:
        obj: parsed by :meth:`dt_sec_ago` into seconds ago
    """
    return round(dt_sec_ago(obj=obj) / 60)


def dt_days_left(obj: Optional[Union[str, timedelta, datetime]]) -> Optional[int]:
    """Get number of days left until a given datetime.

    Args:
        obj: parsed by :meth:`dt_sec_ago` into days left
    """
    if obj:
        obj = dt_parse(obj=obj)
        now = dt_now(tz=obj.tzinfo)
        seconds = (obj - now).total_seconds()
        return round(seconds / 60 / 60 / 24)
    return None


def dt_within_min(
    obj: Union[str, timedelta, datetime],
    n: Optional[Union[str, int]] = None,
) -> bool:
    """Check if given datetime is within the past n minutes.

    Args:
        obj: parsed by :meth:`dt_min_ago` into minutes ago
        n: int of :meth:`dt_min_ago` should be greater than or equal to
    """
    if not is_int(obj=n, digit=True):
        return False

    return dt_min_ago(obj=obj) >= int(n)


def get_path(obj: Union[str, pathlib.Path]) -> pathlib.Path:
    """Convert a str into a fully resolved & expanded Path object.

    Args:
        obj: obj to convert into expanded and resolved absolute Path obj
    """
    return pathlib.Path(obj).expanduser().resolve()


def path_read(
    obj: Union[str, pathlib.Path], binary: bool = False, is_json: bool = False, **kwargs
) -> Union[bytes, str]:
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


def path_write(
    obj: Union[str, pathlib.Path],
    data: Union[bytes, str],
    overwrite: bool = False,
    binary: bool = False,
    binary_encoding: str = "utf-8",
    is_json: bool = False,
    make_parent: bool = True,
    protect_file=0o600,
    protect_parent=0o700,
    **kwargs,
) -> Tuple[pathlib.Path, Callable]:
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
    """Determine the length of the longest string in a list of strings.

    Args:
        obj: list of strings to calculate length of
    """
    return round(max([len(x) + 5 for x in obj]), -1)


def split_str(
    obj: Union[List[str], str],
    split: str = ",",
    strip: Optional[str] = None,
    do_strip: bool = True,
    lower: bool = True,
    empty: bool = False,
) -> List[str]:
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


def echo_ok(msg: str, tmpl: bool = True, **kwargs):
    """Echo a message to console.

    Args:
        msg: message to echo
        tmpl: template to using for echo
        kwargs: passed to ``click.secho``
    """
    echoargs = {}
    echoargs.update(OK_ARGS)
    echoargs.update(kwargs)
    if tmpl:
        msg = OK_TMPL.format(msg=msg)

    LOG.info(msg)
    click.secho(msg, **echoargs)


def echo_warn(msg: str, tmpl: bool = True, **kwargs):
    """Echo a warning message to console.

    Args:
        msg: message to echo
        tmpl: template to using for echo
        kwargs: passed to ``click.secho``
    """
    echoargs = {}
    echoargs.update(WARN_ARGS)
    echoargs.update(kwargs)
    if tmpl:
        msg = WARN_TMPL.format(msg=msg)

    LOG.warning(msg)
    click.secho(msg, **echoargs)


def echo_error(msg: str, abort: bool = True, tmpl: bool = True, **kwargs):
    """Echo an error message to console.

    Args:
        msg: message to echo
        tmpl: template to using for echo
        kwargs: passed to ``click.secho``
        abort: call sys.exit(1) after echoing message
    """
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
    """Gather system information."""
    try:
        cli_args = sys.argv
    except Exception:
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


def calc_percent(part: Union[int, float], whole: Union[int, float], places: int = 2) -> float:
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
    obj: Union[List[dict], dict], listjoin: str = ", ", tmpl: str = "{k}: {v!r}"
) -> List[str]:
    """Join a dictionary into key value strings.

    Args:
        obj: dict or list of dicts to stringify
        listjoin: string to use for joining
        tmpl: template to format key value pairs of dict
    """
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


def get_type_str(obj: Any):
    """Get the type name of a class.

    Args:
        obj: class or tuple of classes to get type name(s) of
    """
    if isinstance(obj, tuple):
        return " or ".join([x.__name__ for x in obj])
    else:
        return obj.__name__


def check_type(value: Any, exp: Any, name: str = "", exp_items: Optional[Any] = None):
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


def check_empty(value: Any, name: str = ""):
    """Check if a value is empty.

    Args:
        value: value to check type of
        name: identifier of what value is for
    """
    if not value:
        vtype = type(value).__name__
        name = f" for {name!r}" if name else ""
        err = f"Required value{name} but received an empty {vtype}: {value!r}"
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


def coerce_str_to_csv(value: str) -> List[str]:
    """Coerce a string into a list of strings.

    Args:
        value: string to seperate using comma
    """
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
    """Parse a string into an IP address.

    Args:
        value: ip address
    """
    try:
        return ipaddress.ip_address(value)
    except Exception as exc:
        raise ToolsError(str(exc))


def parse_ip_network(value: str) -> Union[ipaddress.IPv4Network, ipaddress.IPv6Network]:
    """Parse a string into an IP network.

    Args:
        value: ip network
    """
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


def kv_dump(obj: dict) -> str:
    """Get a string representation of a dictionaries key value pairs.

    Args:
        obj: dictionary to get string of
    """
    return "\n  " + "\n  ".join([f"{k}: {v}" for k, v in obj.items()])


def bom_strip(content: str, strip=True) -> str:
    """Remove the UTF-8 BOM marker from the beginning of a string.

    Args:
        content: string to remove BOM marker from if found
        strip: remove whitespace before & after removing BOM marker
    """
    if strip:
        content = content.strip()
    if content.startswith(codecs.BOM_UTF8.decode()):
        content = content[1:]
    if strip:
        content = content.strip()
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


def check_gui_page_size(size: Optional[int] = None) -> int:
    """Check page size to see if it one of the valid GUI page sizes.

    Args:
        size: page size to check

    Raises:
        :exc:`ApiError`: if size is not one of
            :data:`axonius_api_client.constants.api.GUI_PAGE_SIZES`

    """
    size = size or GUI_PAGE_SIZES[0]
    if size not in GUI_PAGE_SIZES:
        raise ToolsError(f"gui_page_size of {size} is invalid, must be one of {GUI_PAGE_SIZES}")
    return size


def calc_gb(value: Union[str, int], places: int = 2, is_kb: bool = True) -> float:
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
    perc_key: Optional[str] = None,
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


def get_subcls(cls) -> list:
    """Get all subclasses of a class."""
    subs = [s for c in cls.__subclasses__() for s in get_subcls(c)]
    return list(set(cls.__subclasses__()).union(subs))


def prettify_obj(obj, indent=0):
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
    if url_check in obj:
        idx = obj.index(url_check) + len(url_check)
        obj = obj[idx:]
    return obj


def combo_dicts(*args):
    """Pass."""
    ret = {}
    for x in args:
        if isinstance(x, dict):
            ret.update(x)
    return ret
