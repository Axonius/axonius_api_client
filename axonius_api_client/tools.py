# -*- coding: utf-8 -*-
"""Utility tool belt.

Handy wrappers/tools used throughout this package.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
from datetime import datetime, timedelta

import dateutil.parser
import dateutil.relativedelta
import dateutil.tz
import six

from . import constants, exceptions

if not constants.PY37:
    import pathlib2 as pathlib  # pragma: no cover
else:
    import pathlib


def val_type(value, types):
    """Check that value is one of types.

    This is just a handy wrapper for isinstance to throw a wrapped exception.

    Args:
        value (:obj:`object`) -
            Object to check type of
        types (:obj:`tuple` of :class:`type`) -
            Tuple of types

    Raises:
        :exc:`exceptions.ToolsError` -
            When value is not a type of types

    """
    if not isinstance(value, types):
        msg = "Invalid type for value {value!r}, must be one of {types!r}"
        msg = msg.format(value=value, types=types)
        raise exceptions.ToolsError(msg)


def listify(obj, dictkeys=False):
    """Force an object into a list.

    Args:
        obj (:obj:`object`): Object to turn into a list, if object is:

            * :obj:`list` -
                returns as is
            * :obj:`tuple` -
                convert to list
            * :obj:`None` -
                returns as an empty list
            * any of :attr:`axonius_api_client.constants.SIMPLE` -
                return as a list of obj
            * :obj:`dict` -
                * dictkeys is False, returns as a list of obj
                * dictkeys is True, return as a list of keys of obj
        dictkeys (:obj:`bool`, optional) -
                If obj is a dict:

                * True: return obj as a list of keys of obj
                * False: return obj as a list of obj

                Defaults to: ``False``

    Returns:
        :obj:`list`
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
        iterable (:obj:`typing.Iterable`) -
            Iterable to split into chunks of size n
        n (int) -
            Length to split iterable into
        fillvalue (:obj:`None`, optional) -
            Value to fill last chunk with if iterable is not the exact length of n

            Defaults to: ``None``

    Returns:
        :obj:`typing.Iterator`:
            an iterator that returns chunks of length n of the original iterable
    """
    return six.moves.zip_longest(*([iter(iterable)] * n), fillvalue=fillvalue)


def nest_depth(obj):
    """Get the nesting depth of an object.

    This will check to see if how many complex sub-objects a complex object has.

    Examples:
        * A dictionary with any list or dict values would be 1.
        * A list with a dictionary where values are all simple would be 1.
        * A list of lists with simple values would be two.

    Args:
        obj (:obj:`object`) -
            Object to get the nesting depth of.

    Returns:
        :obj:`int`:
            The complexity level of obj
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
        obj (:obj:`object`) -
            Object to convert to int

    Returns:
        :obj:`int`

    Raises:
        :exc:`exceptions.ToolsError`:
            If obj is not able to be converted to int
    """
    try:
        return int(obj)
    except Exception:
        msg = "Supplied value {o!r} is not an integer."
        msg = msg.format(o=obj)
        raise exceptions.ToolsError(msg)


def coerce_bool(obj):
    """Convert an object into bool.

    If obj is a string, will check against constants.YES and constants.NO.

    Args:
        obj (:obj:`object`) -
            Object to convert to bool

    Returns:
        :obj:`bool`

    Raises:
        :exc:`exceptions.ToolsError`:
            If obj is not able to be converted to bool
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
        obj (:obj:`object`) -
            Object to check
        digit (:obj:`bool`, optional) -
            Allow string that is digit to return True

            * True: obj must be (str/bytes where isdigit is True) or int
            * False: obj must be int

            Defaults to: ``False``

    Returns:
        :obj:`bool`

    """
    if digit:
        if isinstance(obj, constants.STR) and obj.isdigit():
            return True

        if isinstance(obj, constants.BYTES) and obj.isdigit():
            return True

    return not isinstance(obj, bool) and isinstance(obj, constants.INT)


def join_url(url, *parts):
    """Join a URL to any number of parts.

    Args:
        url (:obj:`str`) -
            URL to add parts to
        *parts (:obj:`str`) -
            Strings to append to url

    Returns:
        :obj:`str`:
            The url with parts appended

    """
    url = url.rstrip("/") + "/"
    for part in parts:
        if not part:
            continue
        url = url.rstrip("/") + "/"
        part = part.lstrip("/")
        url = six.moves.urllib.parse.urljoin(url, part)
    return url


def join_dot(obj, empty=False, joiner="."):
    """Join a string using periods.

    Args:
        obj (:obj:`object` or :obj:`list` of :obj:`object`) -
            Objects(s) to convert to str and join. Will be coerced into a list.
        empty (:obj:`bool`, optional) -
            Values in constants.EMPTY should not be removed before joining

            * True: Leave values in constants.EMPTY in place
            * False: Remove values in constants.EMPTY

            Defaults to: ``False``
        joiner (:obj:`str`, optional) -
            Value to use when joining obj

            Defaults to: ``"."``

    Returns:
        :obj:`str`
    """
    obj = listify(obj=obj, dictkeys=True)

    if not empty:
        obj = [x for x in obj if x not in constants.EMPTY and format(x)]

    return joiner.join([format(x) for x in obj])


def join_cr(obj, pre=True, post=False, indent="  ", joiner="\n"):
    r"""Create str of elements joined by carriage return.

    Args:
        obj (:obj:`object` or :obj:`list` of :obj:`object`) -
            Objects(s) to convert to str and join. Will be coerced into a list,
            and if obj is dict, keys of dict will be used as obj
        pre (:obj:`bool`, optional) -
            * True: add joiner to the beginning of the joined str
            * False: Do not add joiner to the beginning of the joined str

            Defaults to: ``True``
        post (:obj:`bool`, optional) -
            * True: add joiner to the end of the joined str
            * False: Do not add joiner to the end of the joined str

            Defaults to: ``False``
        indent (:obj:`str`, optional) -
            Value to prefix joiner with before joining str

            Defaults to: ``"  "``
        joiner (:obj:`str`, optional) -
            Value to use when joining obj

            Defaults to: ``"\n"``

    Returns:
        :obj:`str`
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

    Args:
        obj (:obj:`object` or :obj:`list` of :obj:`object`) -
            Objects(s) to convert to str and join. Will be coerced into a list,
            and if obj is dict, keys of dict will be used as obj
        empty (:obj:`bool`, optional) -
            Values in constants.EMPTY should not be removed before joining

            * True: Leave values in constants.EMPTY in place
            * False: Remove values in constants.EMPTY

            Defaults to: ``False``
        indent (:obj:`str`, optional) -
            Value to prefix joiner with before joining str

            Defaults to: ``" "``
        joiner (:obj:`str`, optional) -
            Value to use when joining obj

            Defaults to: ``","``

    Returns:
        :obj:`str`
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
        obj (:obj:`str`) or (:obj:`list` of :obj:`str`) -
            str(s) to strip fix from right side of.
        fix (:obj:`str`) -
            str to remove from obj(s)

    Returns:
        (:obj:`str`) or (:obj:`list` of :obj:`str`)
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
        obj (:obj:`str`) or (:obj:`list` of :obj:`str`) -
            str(s) to strip fix from left side of.
        fix (:obj:`str`) -
            str to remove from obj(s)

    Returns:
        (:obj:`str`) or (:obj:`list` of :obj:`str`)
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
        obj (:obj:`object`) -
            Object to serialize into str format
        indent (:obj:`int`, optional) -
            Make json pretty with this many indents

            Defaults to: ``2``
        sort_keys (:obj:`bool`, optional) -
            * True: Sort keys of dicts
            * False: Leave keys of dicts sorted as is

            Defaults to: ``False``
        error (:obj:`bool`, optional) -
            * True: If json error happens, raise it
            * False: If json error happens, return original obj as is

            Defaults to: ``True``
        **kwargs: Passed to :func:`json.dumps`

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
        obj (:obj:`object`) -
            str to deserialize into obj
        error (:obj:`bool`, optional) -
            * True: If json error happens, raise it
            * False: If json error happens, return original obj as is

            Defaults to: ``True``
        **kwargs: Passed to :func:`json.loads`

    Returns:
        :obj:`object`
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
        obj (:obj:`object`) -
            str to deserialize into obj and then re-serialize back into str
        error (:obj:`bool`, optional) -
            * True: If json error happens, raise it
            * False: If json error happens, return original obj as is

            Defaults to: ``False``
        **kwargs: Passed to :func:`json_dump`

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

    Args:
        obj (:obj:`str` or :obj:`datetime.datetime` or :obj:`datetime.timedelta`) -
            object or list of objects, will be parsed using
            meth:`dateutil.parser.parse` as follows:

            * str: will be parsed into datetime obj
            * timedelta: will be parsed into datetime obj as now - timedelta
            * datetime: will be re-parsed into datetime obj

    Returns:
        :obj:`datetime.datetime`
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
        delta (:obj:`datetime.timedelta`, optional) -
            return the current datetime - supplied timedelta

            Defaults to: ``None``
        tz (:obj:`datetime.timezone`, optional) -
            return the current datetime for a specific timezone

            Defaults to: :obj:`dateutil.tz.tzutc`

    Returns:
        :obj:`datetime.datetime`
    """
    if isinstance(delta, timedelta):
        return dt_parse(obj=delta)

    return datetime.now(tz)


def dt_sec_ago(obj):
    """Get number of seconds ago a given datetime was.

    Args:
        obj (:obj:`object`) -
            will be parsed by :meth:`dt_parse` into a datetime obj

    Returns:
        :obj:`int`
    """
    obj = dt_parse(obj=obj)
    now = dt_now(tz=obj.tzinfo)
    return round((now - obj).total_seconds())


def dt_min_ago(obj):
    """Get number of minutes ago a given datetime was.

    Args:
        obj (:obj:`object`) -
            will be parsed by :meth:`dt_sec_ago` into seconds ago

    Returns:
        :obj:`int`
    """
    return round(dt_sec_ago(obj=obj) / 60)


def dt_within_min(obj, n=None):
    """Check if given datetime is within the past n minutes.

    Args:
        obj (:obj:`object`) -
            will be parsed by :meth:`dt_min_ago` into minutes ago
        n (:obj:`int` or :obj:`str`, optional) -
            int of dt_min_ago(obj) should be greater than or equal to

            Defaults to: ``None``

    Returns:
        :obj:`bool`
    """
    if not is_int(obj=n, digit=True):
        return False

    return dt_min_ago(obj=obj) >= int(n)


def path(obj):
    """Convert a str into a fully resolved & expanded Path object.

    Args:
        obj (:obj:`str` or :obj:`pathlib.Path`) -
            Will convert into expanded and resolved absolute Path obj

    Returns:
        :obj:`pathlib.Path`
    """
    args = {}
    # if not PY35:
    args["strict"] = False
    return pathlib.Path(obj).expanduser().resolve(**args)


def path_read(obj, binary=False, is_json=False, **kwargs):
    """Read data from a file.

    If path filename ends with ".json", deserializes data using :meth:`json_load`.

    Args:
        obj (:obj:`str` or :obj:`pathlib.Path`) -
            path to open - will be parsed by :meth:`path`
        binary (:obj:`bool`, optional) -
            * True: read the data as binary
            * False: read the data as str

            Defaults to: ``False``
        is_json (:obj:`bool`, optional) -
            * True: deserialize data using :meth:`json_load`
            * False: do not deserialize data

            Defaults to: ``False``
        **kwargs: Passed to :meth:`json_load`

    Returns:
        :obj:`tuple` of (:obj:`pathlib.Path`, :obj:`object`)

    Raises:
        :exc:`exceptions.ToolsError`:
            If path does not exist as file
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

    If obj filename ends with ".json", serializes data using :meth:`json_dump`.

    Args:
        obj (:obj:`str` or :obj:`pathlib.Path`) -
            path to open - will be parsed by :meth:`path`
        data (:obj:`str` or :obj:`bytes` or :obj:`object`) -
            data to write to obj
        overwrite (:obj:`bool`, optional) -
            * True: overwrite obj
            * False: do not overwrite obj, raise exception if it already exists

            Defaults to: ``False``
        binary (:obj:`bool`, optional) -
            * True: write the data as binary
            * False: write the data as str

            Defaults to: ``False``
        binary_encoding (:obj:`str`, optional):
            encoding to use when switching from str/bytes

            Defaults to: ``"utf-8"``
        is_json (:obj:`bool`, optional) -
            * True: Serialize data using :meth:`json_load` before writing
            * False: Do not serialize data before writing

            Defaults to: ``False``
        make_parent (:obj:`bool`, optional) -
            * True: If the parent directory does not exist, create it
            * False: If the parent directory does not exist, raise exception

            Defaults to: ``True``
        protect_file (:obj:`oct`) -
            octal mode of permissions to set on file

            Defaults to: ``0o600`` (read/write to owner only)
        protect_dir (:obj:`oct`) -
            octal mode of permissions to set on parent directory when creating

            Defaults to: ``0o700`` (read/write/execute to owner only)
        **kwargs: Passed to :meth:`json_dump`

    Returns:
        :obj:`tuple` of (:obj:`pathlib.Path`, method):
            tuple of (resolved path obj, method used to write data to file)

    Raises:
        :exc:`exceptions.ToolsError`:
            If path exists as file and overwrite is False or if
            parent path does not exist and make_parent is False
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
