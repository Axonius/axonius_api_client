# -*- coding: utf-8 -*-
"""Axonius API Client utility tools module."""
from __future__ import absolute_import, division, print_function, unicode_literals

import json
from datetime import datetime, timedelta

import dateutil.parser
import dateutil.relativedelta
import dateutil.tz
import six

from . import exceptions

if six.PY2:
    import pathlib2 as pathlib  # pragma: no cover
else:
    import pathlib


COMPLEX = (dict, list, tuple)
EMPTY = [None, "", [], {}, ()]
LIST = (tuple, list)
STR = six.string_types
INT = six.integer_types
BYTES = six.binary_type
SIMPLE = tuple(list(STR) + [int, bool, float])
SIMPLE_NONE = tuple(list(SIMPLE) + [None])
YES = [True, 1, "1", "true", "t", "yes", "y", "yas"]
NO = [False, 0, "0", "false", "f", "no", "n", "noes"]


def listify(obj, dictkeys=False):
    """Pass."""
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


def grouper(iterable, n, fillvalue=None):
    """Chunk up iterables."""
    return six.moves.zip_longest(*([iter(iterable)] * n), fillvalue=fillvalue)


def nest_depth(obj):
    """Pass."""
    if isinstance(obj, dict):
        obj = list(obj.values())

    if isinstance(obj, LIST):
        calcs = [nest_depth(obj=x) for x in obj if isinstance(obj, COMPLEX)]
        if calcs:
            return 1 + max(calcs)
        return 1
    return 0


def coerce_int(obj):
    """Pass."""
    try:
        return int(obj)
    except Exception:
        msg = "Supplied value {o!r} is not an integer."
        msg = msg.format(o=obj)
        raise exceptions.ToolsError(msg)


def coerce_bool(obj):
    """Pass."""
    coerce_obj = obj

    if isinstance(obj, STR):
        coerce_obj.lower().strip()

    if coerce_obj in YES:
        return True

    if coerce_obj in NO:
        return False

    msg = "Supplied value {o!r} is not one of {y} for true or {n} for false."
    msg = msg.format(o=coerce_obj, y=YES, n=NO)
    raise exceptions.ToolsError(msg)


def is_int(obj, digit=False):
    """Pass."""
    if digit:
        if isinstance(obj, STR) and obj.isdigit():
            return True

        if isinstance(obj, BYTES) and obj.isdigit():
            return True

    return not isinstance(obj, bool) and isinstance(obj, INT)


def join_url(url, *parts):
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


def join_dot(obj, empty=False, joiner="."):
    """Pass."""
    obj = listify(obj=obj, dictkeys=True)

    if not empty:
        obj = [x for x in obj if x not in EMPTY and format(x)]

    return joiner.join([format(x) for x in obj])


def join_cr(obj, pre=True, post=False, indent="  ", joiner="\n"):
    """Pass."""
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
    """Pass."""
    obj = listify(obj=obj, dictkeys=True)

    if not empty:
        obj = [x for x in obj if x not in EMPTY and format(x)]

    if indent:
        joiner = "{}{}".format(joiner, indent)

    return joiner.join([format(x) for x in obj])


def strip_right(obj, fix):
    """Pass."""
    if isinstance(obj, LIST) and all([isinstance(x, STR) for x in obj]):
        return [strip_right(obj=x, fix=fix) for x in obj]

    if isinstance(obj, STR):
        plen = len(fix)

        if obj.endswith(fix):
            return obj[:-plen]

    return obj


def strip_left(obj, fix):
    """Pass."""
    if isinstance(obj, LIST) and all([isinstance(x, STR) for x in obj]):
        return [strip_left(obj=x, fix=fix) for x in obj]

    if isinstance(obj, STR):
        plen = len(fix)

        if obj.startswith(fix):
            return obj[plen:]

    return obj


def json_dump(obj, indent=2, sort_keys=False, error=True, **kwargs):
    """Pass."""
    try:
        return json.dumps(obj, indent=indent, sort_keys=sort_keys, **kwargs)
    except Exception:
        if error:
            raise
        return obj


def json_load(obj, error=True, **kwargs):
    """Pass."""
    try:
        return json.loads(obj, **kwargs)
    except Exception:
        if error:
            raise
        return obj


def json_reload(obj, error=False, **kwargs):
    """Pass."""
    obj = json_load(obj=obj, error=error)
    if not isinstance(obj, STR):
        obj = json_dump(obj=obj, error=error, **kwargs)
    obj = obj or ""
    if isinstance(obj, STR):
        obj = obj.strip()
    return obj


def dt_parse(obj):
    """Pass."""
    if isinstance(obj, LIST) and all([isinstance(x, STR) for x in obj]):
        return [dt_parse(obj=x) for x in obj]

    if isinstance(obj, datetime):
        obj = format(obj)

    if isinstance(obj, timedelta):
        obj = format(dt_now() - obj)

    return dateutil.parser.parse(obj)


def dt_now(delta=None, tz=dateutil.tz.tzutc()):
    """Pass."""
    if isinstance(delta, timedelta):
        return dt_parse(obj=delta)

    return datetime.now(tz)


def dt_sec_ago(obj):
    """Pass."""
    obj = dt_parse(obj=obj)
    now = dt_now(tz=obj.tzinfo)
    return round((now - obj).total_seconds())


def dt_min_ago(obj):
    """Pass."""
    return round(dt_sec_ago(obj=obj) / 60)


def dt_within_min(obj, n=None):
    """Pass."""
    if not is_int(obj=n, digit=True):
        return False

    return dt_min_ago(obj=obj) >= int(n)


def path(obj):
    """Pass."""
    return pathlib.Path(obj).expanduser().resolve(strict=False)


def path_read(obj, binary=False, is_json=False, **kwargs):
    """Pass."""
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

    if robj.suffix == ".json" and isinstance(data, STR):
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
    """Pass."""
    obj = path(obj=obj)

    if is_json:
        data = json_dump(obj=data, **kwargs)

    if obj.suffix == ".json" and not isinstance(data, STR):
        kwargs.setdefault("error", False)
        data = json_dump(obj=data, **kwargs)

    if binary:
        if not isinstance(data, BYTES):
            data = data.encode(binary_encoding)
        method = obj.write_bytes
    else:
        if isinstance(data, BYTES):
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
