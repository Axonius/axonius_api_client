# -*- coding: utf-8 -*-
"""Axonius API Client utility tools module."""
from __future__ import absolute_import, division, print_function, unicode_literals

import csv as _csv
import datetime
import json as _json

import dateutil.parser
import dateutil.relativedelta
import dateutil.tz
import six

if six.PY2:
    import pathlib2 as pathlib  # pragma: no cover
else:
    import pathlib


class is_type(object):
    """Pass."""

    @staticmethod
    def str(obj):
        """Pass."""
        return isinstance(obj, six.string_types)

    @staticmethod
    def int(obj):
        """Pass."""
        return isinstance(obj, six.integer_types)

    @staticmethod
    def dict(obj):
        """Pass."""
        return isinstance(obj, dict)

    @staticmethod
    def list(obj):
        """Pass."""
        return isinstance(obj, (list, tuple))

    @staticmethod
    def float(obj):
        """Pass."""
        return isinstance(obj, float)

    @staticmethod
    def none(obj):
        """Pass."""
        return obj is None

    @staticmethod
    def empty(obj):
        """Pass."""
        return obj in [None, "", [], {}, ()]

    @staticmethod
    def bool(obj):
        """Pass."""
        return isinstance(obj, bool)

    @staticmethod
    def simple(obj):
        """Pass."""
        return (
            is_type.str(obj)
            or is_type.int(obj)
            or is_type.bool(obj)
            or is_type.float(obj)
            or is_type.none(obj)
        )

    @staticmethod
    def lot(obj, t):
        """Pass."""
        if not is_type.list(obj):
            return False
        for x in obj:
            if not t(x):
                return False
        return True

    @staticmethod
    def los(obj):
        """Pass."""
        return is_type.lot(obj, is_type.simple)

    @staticmethod
    def lod(obj):
        """Pass."""
        return is_type.lot(obj, is_type.dict)

    @staticmethod
    def lol(obj):
        """Pass."""
        return is_type.lot(obj, is_type.list)

    @staticmethod
    def lols(obj):
        """Pass."""
        if not is_type.lol(obj):
            return False

        for x in obj:
            if not is_type.los(x):
                return False
        return True


class path(object):
    """Pass."""

    @staticmethod
    def resolve(obj):
        """Pass."""
        return pathlib.Path(obj).absolute().resolve()

    @staticmethod
    def read(obj, binary=False, is_json=False):
        """Pass."""
        obj = path.resolve(obj)
        data = obj.read_bytes() if binary else obj.read_text()

        if obj.suffix == ".json":
            try:
                return json.load(data)
            except Exception:
                return data

        if is_json:
            return json.load(data)

        return data

    @staticmethod
    def write(obj, data, binary=False, is_json=False, **kwargs):
        """Pass."""
        obj = path.resolve(obj)

        method = obj.write_bytes if binary else obj.write_text

        if obj.suffix == ".json" and not is_type.str(data):
            kwargs.setdefault("error", False)
            return method(json.cereal(data, **kwargs))

        if is_json and not is_type.str(data):
            return method(json.cereal(data, **kwargs))

        return method(data)


class join(object):
    """Pass."""

    @staticmethod
    def url(url, *parts):
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

    @staticmethod
    def dot(*obj):
        """Pass."""
        return ".".join([format(x) for x in obj if format(x)])

    @staticmethod
    def cr(obj, indent=0, pre=True):
        """Pass."""
        joiner = "\n{}".format(" " * indent)
        joined = joiner.join([format(x) for x in listify(obj)])
        if pre and joined:
            return joiner + joined
        return joined

    @staticmethod
    def csv(obj, space=True):
        """Pass."""
        joiner = ", " if space else ","
        return joiner.join([format(x) for x in listify(obj)])


class strip(object):
    """Pass."""

    @staticmethod
    def right(obj, postfix):
        """Pass."""
        if is_type.list(obj):
            obj = [strip.right(x, postfix) for x in obj]
        elif is_type.str(obj):
            plen = len(postfix)
            obj = obj[:-plen] if obj.endswith(postfix) else obj
        return obj

    @staticmethod
    def left(obj, prefix):
        """Pass."""
        if is_type.list(obj):
            return [strip.left(obj=x, prefix=prefix) for x in obj]
        elif is_type.str(obj):
            plen = len(prefix)
            return obj[plen:] if obj.startswith(prefix) else obj
        return obj


class json(object):
    """Pass."""

    @staticmethod
    def cereal(obj, indent=2, sort_keys=False, **kwargs):
        """Pass."""
        error = kwargs.pop("error", True)
        try:
            return _json.dumps(obj, indent=indent, sort_keys=sort_keys, **kwargs)
        except Exception:
            if error:
                raise
            return obj

    @staticmethod
    def toast(obj, **kwargs):
        """Pass."""
        return _json.loads(obj, **kwargs)

    @staticmethod
    def butter(text, **kwargs):
        """Pass."""
        try:
            return (json.cereal(json.toast(text), **kwargs) or "").strip()
        except Exception:
            return text or ""


class dt(object):
    """Pass."""

    @staticmethod
    def parse(obj, err=False):
        """Pass."""
        if is_type.list(obj):
            return [dt.parse(x, err) for x in obj]
        try:
            return dateutil.parser.parse(obj)
        except Exception:
            if err:
                raise
            return obj

    @staticmethod
    def minutes_ago(then):
        """Pass."""
        now = datetime.datetime.now(dateutil.tz.tzutc())
        then = dateutil.parser.parse(then)
        return round((now - then).total_seconds() / 60)


# FUTURE: Add logging about unhandled bits...
class csv(object):
    """Pass."""

    QUOTING = _csv.QUOTE_NONNUMERIC

    @classmethod
    def cereal(
        cls,
        rows,
        stream=None,
        compress=False,
        headers=None,
        stream_value=True,
        **kwargs
    ):
        """Pass."""
        rows = cls.compress(rows) if compress else rows

        kwargs.setdefault("quoting", cls.QUOTING)
        kwargs.setdefault("f", stream or six.StringIO())
        kwargs["fieldnames"] = kwargs.get("fieldnames", headers or [])

        if not kwargs["fieldnames"]:
            for row in rows:
                for key in row:
                    if key not in kwargs["fieldnames"]:
                        kwargs["fieldnames"].append(key)

        writer = _csv.DictWriter(**kwargs)

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

        if stream_value:
            return kwargs["f"].getvalue()

        return kwargs["f"]

    @classmethod
    def _compress_complex(cls, item, pre):
        """Pass."""
        new_item = {}

        if is_type.dict(item):
            for k in list(item):
                k_pre = join.dot(pre, k)

                if is_type.simple(item[k]) or is_type.los(item[k]):
                    new_item[k_pre] = join.cr(item.pop(k), pre=False)
                    continue

                new_sub_item = cls._compress_complex(item[k], k_pre)
                new_item.update(new_sub_item)

                if not item[k]:
                    item.pop(k)

            return new_item

        if is_type.lod(item):
            for idx, sub_item in enumerate(list(item)):
                k_pre = join.dot(pre, idx)

                new_sub_item = cls._compress_complex(sub_item, k_pre)
                new_item.update(new_sub_item)
                if not sub_item:
                    item.remove(sub_item)
            return new_item

        if is_type.lols(item):
            new_sub_item = []

            for sub_item in list(item):
                new_sub_item.append(join.cr(sub_item, pre=False))
                item.remove(sub_item)

            new_item[pre] = join.cr(new_sub_item, pre=False)
            return new_item

        if is_type.lol(item):
            for idx, sub_item in enumerate(list(item)):
                k_pre = join.dot(pre, idx)

                if is_type.los(sub_item):
                    new_item[k_pre] = join.cr(sub_item, pre=False)
                    item.remove(sub_item)
            return new_item

        return new_item

    @classmethod
    def compress_dict(cls, item):
        """Pass."""
        new_item = {}

        for k in list(item):
            if is_type.simple(item[k]) or is_type.los(item[k]):
                new_item[k] = join.cr(item.pop(k), pre=False)
                continue

            new_complex = cls._compress_complex(item[k], k)
            new_item.update(new_complex)

            if not item[k]:
                item.pop(k)

        return new_item

    @classmethod
    def compress(cls, items):
        """Pass."""
        return [cls.compress_dict(x) for x in items]


def listify(obj):
    """Pass."""
    if is_type.list(obj):
        return list(obj)
    if is_type.none(obj):
        return []
    if is_type.simple(obj):
        return [obj]
    if is_type.dict(obj):
        return list(obj)
    return obj


def grouper(iterable, n, fillvalue=None):
    """Chunk up iterables."""
    args = [iter(iterable)] * n
    return six.moves.zip_longest(*args, fillvalue=fillvalue)
