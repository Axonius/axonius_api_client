# -*- coding: utf-8 -*-
"""Axonius API Client utility tools module."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json

import dateutil.parser
import dateutil.tz
import dateutil.relativedelta

import six

if six.PY2:
    import pathlib2 as pathlib  # pragma: no cover
else:
    import pathlib

STR = six.string_types
INT = six.integer_types
SIMPLE = tuple(list(STR) + list(INT))
LIST = (list, tuple)


def is_dict(obj):
    """Pass."""
    return isinstance(obj, dict)


def is_list(obj):
    """Pass."""
    return isinstance(obj, LIST)


def is_simple(obj):
    """Pass."""
    return isinstance(obj, SIMPLE)


def is_list_of_simple(obj, or_simple=False):
    """Pass."""
    if or_simple and is_simple(obj):
        return True

    if is_list(obj):
        return all([is_simple(x) for x in obj])

    return False


def is_list_of_dict(obj):
    """Pass."""
    return is_list(obj) and all([is_dict(x) for x in obj])


def listify(obj, otype=SIMPLE, oempty=True, itype=SIMPLE):
    """Pass."""
    if obj in [None, ""]:
        return []

    if otype and not isinstance(obj, LIST):
        if isinstance(obj, otype):
            obj = [obj]
        elif oempty:
            obj = []

    if not isinstance(obj, LIST):
        obj = [obj]

    if itype:
        obj = [i for i in obj if isinstance(i, itype)]
    return obj


def resolve_path(path):
    """Pass."""
    return pathlib.Path(path).absolute().resolve()


def urljoin(url, *parts):
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


def grouper(iterable, n, fillvalue=None):
    """Chunk up iterables."""
    args = [iter(iterable)] * n
    return six.moves.zip_longest(*args, fillvalue=fillvalue)


def rstrip(obj, postfix):
    """Pass."""
    if isinstance(obj, LIST):
        obj = [rstrip(x, postfix) for x in obj]
    elif isinstance(obj, STR):
        plen = len(postfix)
        obj = obj[:-plen] if obj.endswith(postfix) else obj
    return obj


def lstrip(obj, prefix):
    """Pass."""
    if isinstance(obj, LIST):
        obj = [lstrip(obj=x, prefix=prefix) for x in obj]
    elif isinstance(obj, STR):
        plen = len(prefix)
        obj = obj[plen:] if obj.startswith(prefix) else obj
    return obj


def to_json(obj, **kwargs):
    """Pass."""
    kwargs.setdefault("indent", 2)
    return json.dumps(obj, **kwargs)


def json_pretty(text):
    """Pass."""
    try:
        text = to_json(json.loads(text))
    except Exception:
        text = text or ""
    return (text or "").strip()


def _join(obj, j, pre=""):
    """Pass."""
    if isinstance(obj, dict):
        obj = list(obj)
    if isinstance(obj, SIMPLE):
        obj = [obj]
    return pre + j.join([format(x) for x in obj])


def crjoin(obj, j="\n  ", pre="\n  "):
    """Pass."""
    return _join(obj=obj, j=j, pre=pre)


def csvjoin(obj, j=", ", pre=""):
    """Pass."""
    return _join(obj=obj, j=j, pre=pre)


def dt_parse(dt, err=False):
    """Pass."""
    if isinstance(dt, LIST):
        return [dt_parse(x, err) for x in dt]
    try:
        return dateutil.parser.parse(dt)
    except Exception:
        if err:
            raise
        return dt


def dt_minutes_ago(then):
    """Pass."""
    now = datetime.datetime.now(dateutil.tz.tzutc())
    then = dateutil.parser.parse(then)
    return round((now - then).total_seconds() / 60)


# FUTURE: use or lose
'''

def dt_delta(then):
    """Pass."""
    now = datetime.datetime.now(dateutil.tz.tzutc())
    then = dt_parse(then)
    return dateutil.relativedelta.relativedelta(now, then)


def dt_ago(hours=0, minutes=0, seconds=0, strip_ms=True):
    """Pass."""
    now = datetime.datetime.now(dateutil.tz.tzutc())
    delta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    then = now - delta
    return then.replace(microsecond=0) if strip_ms else then

'''
