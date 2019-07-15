# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import six


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
