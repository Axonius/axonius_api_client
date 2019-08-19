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
    if isinstance(obj, (list, tuple)):
        obj = [rstrip(x, postfix) for x in obj]
    elif isinstance(obj, six.string_types):
        plen = len(postfix)
        obj = obj[:-plen] if obj.endswith(postfix) else obj
    return obj


def lstrip(obj, prefix):
    """Pass."""
    if isinstance(obj, (list, tuple)):
        obj = [lstrip(obj=x, prefix=prefix) for x in obj]
    elif isinstance(obj, six.string_types):
        plen = len(prefix)
        obj = obj[plen:] if obj.startswith(prefix) else obj
    return obj


def json_pretty(text):
    """Pass."""
    try:
        text = json.dumps(json.loads(text), indent=2)
    except Exception:
        text = text or ""
    text = (text or "").strip()
    return text


def _join(obj, j, pre=""):
    """Pass."""
    if isinstance(obj, dict):
        obj = list(obj.keys())
    if isinstance(obj, str):
        obj = [obj]
    obj = [format(x) for x in obj]
    return pre + j.join(obj)


def crjoin(obj, j="\n  ", pre="\n  "):
    """Pass."""
    return _join(obj=obj, j=j, pre=pre)


def csvjoin(obj, j=", ", pre=""):
    """Pass."""
    return _join(obj=obj, j=j, pre=pre)


def dt_parse(dt, err=False):
    """Pass."""
    if isinstance(dt, (list, tuple)):
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
