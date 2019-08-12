# -*- coding: utf-8 -*-
"""Axonius API Client utility tools module."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

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


def crjoin(obj, j="\n  "):
    """Pass."""
    return _join(obj=obj, j=j, pre=j)


def csvjoin(obj, j=", "):
    """Pass."""
    return _join(obj=obj, j=j)
