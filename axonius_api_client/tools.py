# -*- coding: utf-8 -*-
"""Utilities and tools."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
from datetime import datetime, timedelta

import dateutil.parser
import dateutil.relativedelta
import dateutil.tz

from . import constants, exceptions

# pathlib in python lower than 3.7 does not support args we use
if not constants.PY37:
    try:
        import pathlib2 as pathlib  # pragma: no cover
    except Exception:  # pragma: no cover
        import pathlib
else:
    import pathlib

if constants.PY3:
    from itertools import zip_longest
    from urllib.parse import urljoin
else:
    from itertools import izip_longest as zip_longest
    from urlparse import urljoin


def val_type(value, types):
    """Check that value is one of types.

    Notes:
        * handy wrapper for isinstance to throw a wrapped exception

    Args:
        value (:obj:`object`): object to check type of
        types (:obj:`tuple` of :class:`type`): tuple of types

    Raises:
        :exc:`exceptions.ToolsError`: if value is not an instance of types

    """
    if not isinstance(value, types):
        msg = "Invalid type for value {value!r}, must be one of {types!r}"
        msg = msg.format(value=value, types=types)
        raise exceptions.ToolsError(msg)


def listify(obj, dictkeys=False):
    """Force an object into a list.

    Notes:
        * :obj:`list`: returns as is
        * :obj:`tuple`: convert to list
        * :obj:`None`: returns as an empty list
        * any of :data:`axonius_api_client.constants.SIMPLE`: return as a list of obj
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

    if isinstance(obj, constants.SIMPLE):
        return [obj]

    if isinstance(obj, dict):
        if dictkeys:
            return list(obj)

        return [obj]

    return obj


def grouper(iterable, n, fillvalue=None):
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


def nest_depth(obj):
    """Get the nesting depth of an object.

    Notes:
        * checks to see if how many complex sub-objects an object has.
        * dictionary with any list or dict values would be 1.
        * list with a dictionary where values are all simple would be 1.
        * list of lists with simple values would be two.

    Args:
        obj (:obj:`object`): object to get the nesting depth of

    Returns:
        :obj:`int`: int of the complexity level of obj
    """
    if isinstance(obj, dict):
        obj = list(obj.values())

    if isinstance(obj, constants.LIST):
        calcs = [nest_depth(obj=x) for x in obj if isinstance(obj, constants.COMPLEX)]
        if calcs:
            return 1 + max(calcs)
        return 1
    return 0


def coerce_int(obj):
    """Convert an object into int.

    Args:
        obj (:obj:`object`): object to convert to int

    Returns:
        :obj:`int`: coerced int

    Raises:
        :exc:`exceptions.ToolsError`: if obj is not able to be converted to int
    """
    try:
        return int(obj)
    except Exception:
        msg = "Supplied value {o!r} is not an integer."
        msg = msg.format(o=obj)
        raise exceptions.ToolsError(msg)


def coerce_bool(obj):
    """Convert an object into bool.

    Notes:
        * if obj is str, will check against :data:`axonius_api_client.constants.YES`
          and :data:`axonius_api_client.constants.NO`

    Args:
        obj (:obj:`object`): object to coerce to bool

    Returns:
        :obj:`bool`: coerced bool

    Raises:
        :exc:`exceptions.ToolsError`: obj is not able to be converted to bool
    """
    coerce_obj = obj

    if isinstance(obj, constants.STR):
        coerce_obj = coerce_obj.lower().strip()

    if coerce_obj in constants.YES:
        return True

    if coerce_obj in constants.NO:
        return False

    msg = "Supplied value {o!r} is not one of {y} for true or {n} for false."
    msg = msg.format(o=coerce_obj, y=constants.YES, n=constants.NO)
    raise exceptions.ToolsError(msg)


def is_int(obj, digit=False):
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
        if (
            isinstance(obj, constants.STR) or isinstance(obj, constants.BYTES)
        ) and obj.isdigit():
            return True

    return not isinstance(obj, bool) and isinstance(obj, constants.INT)


def join_url(url, *parts):
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


def join_dot(obj, empty=False, joiner="."):
    """Join a string using periods.

    Notes:
        * obj will be coerced into a list
        * if obj is dict, keys of dict will be used as obj

    Args:
        obj (:obj:`object` or :obj:`list` of :obj:`object`): objects(s) to convert
            to str and join.
        empty (:obj:`bool`, optional): default ``False`` -

            * if ``True`` leave values in constants.EMPTY in place
            * if ``false`` remove values in constants.EMPTY
        joiner (:obj:`str`, optional): default ``"."`` - value to use when joining obj

    Returns:
        :obj:`str`: str of obj joined using joiner
    """
    obj = listify(obj=obj, dictkeys=True)

    if not empty:
        obj = [x for x in obj if x not in constants.EMPTY and format(x)]

    return joiner.join([format(x) for x in obj])


def join_cr(obj, pre=True, post=False, indent="  ", joiner="\n"):
    r"""Create str of elements joined by carriage return.

    Notes:
        * obj will be coerced into a list
        * if obj is dict, keys of dict will be used as obj

    Args:
        obj (:obj:`object` or :obj:`list` of :obj:`object`): objects(s) to convert to
            str and join
        pre (:obj:`bool`, optional): default ``True`` -

            * if ``True`` add joiner to the beginning of the joined str
            * if ``False`` do not add joiner to the beginning of the joined str

        post (:obj:`bool`, optional): default ``False`` -

            * if ``True`` add joiner to the end of the joined str
            * if ``False`` do not add joiner to the end of the joined str
        indent (:obj:`str`, optional): default ``"  "`` - value to prefix joiner
        joiner (:obj:`str`, optional): default ``"\n"`` - value to use when joining obj

    Returns:
        :obj:`str`: str of obj joined using joiner
    """
    obj = listify(obj=obj, dictkeys=True)

    if indent:
        joiner = "{}{}".format(joiner, indent)

    joined = joiner.join([format(x) for x in obj])

    if joined:
        if pre:
            joined = joiner + joined
        if post:
            joined = joined + joiner

    return joined


def join_comma(obj, empty=False, indent=" ", joiner=","):
    """Create str of elements joined by comma.

    Notes:
        * obj will be coerced into a list
        * if obj is dict, keys of dict will be used as obj

    Args:
        obj (:obj:`object` or :obj:`list` of :obj:`object`): objects(s) to convert
            to str and join.
        empty (:obj:`bool`, optional): default ``False`` -

            * if ``True`` leave values in constants.EMPTY in place
            * if ``False`` remove values in constants.EMPTY
        indent (:obj:`str`, optional): default ``"  "`` - value to prefix joiner
        joiner (:obj:`str`, optional): default ``","`` - value to use when joining obj

    Returns:
        :obj:`str`: str of obj joined using joiner
    """
    obj = listify(obj=obj, dictkeys=True)

    if not empty:
        obj = [x for x in obj if x not in constants.EMPTY and format(x)]

    if indent:
        joiner = "{}{}".format(joiner, indent)

    return joiner.join([format(x) for x in obj])


def strip_right(obj, fix):
    """Strip text from the right side of obj.

    Args:
        obj (:obj:`str`) or (:obj:`list` of :obj:`str`): str(s) to strip fix from
        fix (:obj:`str`): str to remove from obj(s)

    Returns:
        (:obj:`str`) or (:obj:`list` of :obj:`str`): obj with fix stripped
    """
    if isinstance(obj, constants.LIST) and all(
        [isinstance(x, constants.STR) for x in obj]
    ):
        return [strip_right(obj=x, fix=fix) for x in obj]

    if isinstance(obj, constants.STR):
        plen = len(fix)

        if obj.endswith(fix):
            return obj[:-plen]

    return obj


def strip_left(obj, fix):
    """Strip text from the left side of obj.

    Args:
        obj (:obj:`str`) or (:obj:`list` of :obj:`str`): str(s) to strip fix from
        fix (:obj:`str`): str to remove from obj(s)

    Returns:
        (:obj:`str`) or (:obj:`list` of :obj:`str`): obj with fix stripped
    """
    if isinstance(obj, constants.LIST) and all(
        [isinstance(x, constants.STR) for x in obj]
    ):
        return [strip_left(obj=x, fix=fix) for x in obj]

    if isinstance(obj, constants.STR):
        plen = len(fix)

        if obj.startswith(fix):
            return obj[plen:]

    return obj


def json_dump(obj, indent=2, sort_keys=False, error=True, **kwargs):
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
    try:
        return json.dumps(obj, indent=indent, sort_keys=sort_keys, **kwargs)
    except Exception:
        if error:
            raise
        return obj


def json_load(obj, error=True, **kwargs):
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


def json_reload(obj, error=False, **kwargs):
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
    if not isinstance(obj, constants.STR):
        obj = json_dump(obj=obj, error=error, **kwargs)
    obj = obj or ""
    if isinstance(obj, constants.STR):
        obj = obj.strip()
    return obj


def dt_parse(obj):
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
    if isinstance(obj, constants.LIST) and all(
        [isinstance(x, constants.STR) for x in obj]
    ):
        return [dt_parse(obj=x) for x in obj]

    if isinstance(obj, datetime):
        obj = format(obj)

    if isinstance(obj, timedelta):
        obj = format(dt_now() - obj)

    return dateutil.parser.parse(obj)


def dt_now(delta=None, tz=dateutil.tz.tzutc()):
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


def dt_sec_ago(obj):
    """Get number of seconds ago a given datetime was.

    Args:
        obj (:obj:`object`): will be parsed by :meth:`dt_parse` into a datetime obj

    Returns:
        :obj:`int`:
            int of secs ago obj was
    """
    obj = dt_parse(obj=obj)
    now = dt_now(tz=obj.tzinfo)
    return round((now - obj).total_seconds())


def dt_min_ago(obj):
    """Get number of minutes ago a given datetime was.

    Args:
        obj (:obj:`object`): will be parsed by :meth:`dt_sec_ago` into seconds ago

    Returns:
        :obj:`int`: int of minutes ago obj was
    """
    return round(dt_sec_ago(obj=obj) / 60)


def dt_within_min(obj, n=None):
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


def path(obj):
    """Convert a str into a fully resolved & expanded Path object.

    Args:
        obj (:obj:`str` or :obj:`pathlib.Path`): obj to convert into
            expanded and resolved absolute Path obj

    Returns:
        :obj:`pathlib.Path`: resolved path
    """
    args = {}
    # if not PY35:
    args["strict"] = False
    return pathlib.Path(obj).expanduser().resolve(**args)


def path_read(obj, binary=False, is_json=False, **kwargs):
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
        :exc:`exceptions.ToolsError`: path does not exist as file
    """
    robj = path(obj=obj)

    if not robj.is_file():
        msg = "Supplied path='{o}' (resolved='{ro}') does not exist!"
        msg = msg.format(o=obj, ro=robj)
        raise exceptions.ToolsError(msg)

    if binary:
        data = robj.read_bytes()
    else:
        data = robj.read_text()

    if is_json:
        data = json_load(obj=data, **kwargs)

    if robj.suffix == ".json" and isinstance(data, constants.STR):
        kwargs.setdefault("error", False)
        data = json_load(obj=data, **kwargs)

    return robj, data


def path_write(
    obj,
    data,
    overwrite=False,
    binary=False,
    binary_encoding="utf-8",
    is_json=False,
    make_parent=True,
    protect_file=0o600,
    protect_parent=0o700,
    # fmt: off
    **kwargs
    # fmt: on
):
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
        :exc:`exceptions.ToolsError`: path exists as file and overwrite is False
        :exc:`exceptions.ToolsError`: if parent path does not exist and make_parent
            is False
    """
    obj = path(obj=obj)

    if is_json:
        data = json_dump(obj=data, **kwargs)

    if obj.suffix == ".json" and not (
        isinstance(data, constants.STR) or isinstance(data, constants.BYTES)
    ):
        kwargs.setdefault("error", False)
        data = json_dump(obj=data, **kwargs)

    if binary:
        if isinstance(data, constants.STR):
            data = data.encode(binary_encoding)
        method = obj.write_bytes
    else:
        if isinstance(data, constants.BYTES):
            data = data.decode(binary_encoding)
        method = obj.write_text

    if obj.is_file() and overwrite is False:
        error = "File '{path}' already exists and overwrite is False"
        error = error.format(path=format(obj))
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


# def is_simple(obj):
#     """Is simple."""
#     return isinstance(obj, constants.SIMPLE) or o is None


# def is_list(obj):
#     """Is simple."""
#     return isinstance(obj, constants.LIST)


# def is_los(o):
#     """Is simple or list of simples."""
#     return is_simple(o) or (is_list(o) and all([is_simple(x) for x in o]))


# def is_dos(o):
#     """Is dict with simple or list of simple values."""
#     return isinstance(o, dict) and all([is_los(v) for v in o.values()])


def kwdump(obj, join=", ", pre=""):
    """Pass."""
    return pre + join.join(["{}:{!r}".format(k, v) for k, v in obj.items()])


def longest_str(obj):
    """Badwolf."""
    return round(max([len(x) + 5 for x in obj]), -1)


def split_str(obj, split=",", strip=None, do_strip=True, lower=True, empty=False):
    """Split a string or list of strings into a list of strings."""
    if isinstance(obj, constants.LIST):
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
