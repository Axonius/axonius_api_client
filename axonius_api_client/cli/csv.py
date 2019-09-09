# -*- coding: utf-8 -*-
"""Axonius API Client utility tools module."""
from __future__ import absolute_import, division, print_function, unicode_literals

import copy
import csv

import six

from .. import exceptions, tools

QUOTING = csv.QUOTE_NONNUMERIC


def listofdict(
    rows, stream=None, compress=False, headers=None, stream_value=True, **kwargs
):
    """Pass."""
    rows = copy.deepcopy(rows)

    if compress:
        rows = [compress_dict(obj=x) for x in rows]

    kwargs.setdefault("quoting", QUOTING)
    kwargs.setdefault("f", stream or six.StringIO())
    kwargs["fieldnames"] = kwargs.get("fieldnames", headers or [])

    if not kwargs["fieldnames"]:
        for row in rows:
            for key in row:
                if key not in kwargs["fieldnames"]:
                    kwargs["fieldnames"].append(key)

    writer = csv.DictWriter(**kwargs)

    writer.writeheader()

    for row in rows:
        writer.writerow(row)

    if stream_value:
        return kwargs["f"].getvalue()

    return kwargs["f"]


def compress_dict(obj):
    """Pass."""
    new_item = {}

    for k in list(obj):
        if isinstance(obj[k], tools.SIMPLE):
            new_item[k] = tools.join_cr(obj=obj.pop(k), pre=False, indent=None)
            continue

        if isinstance(obj[k], tools.LIST) and all(
            [isinstance(x, tools.SIMPLE) for x in obj[k]]
        ):
            new_item[k] = tools.join_cr(obj=obj.pop(k), pre=False, indent=None)
            continue

        new_complex = _complex(obj=obj[k], pre=k)
        new_item.update(new_complex)

        if not obj[k]:
            obj.pop(k)

    return new_item


def _dict(obj, pre):
    """Pass."""
    new_obj = {}

    for k in list(obj):
        k_pre = tools.join_dot(obj=[pre, k])

        if isinstance(obj[k], tools.SIMPLE):
            new_obj[k_pre] = tools.join_cr(obj=obj.pop(k), pre=False, indent=None)
            continue

        if isinstance(obj[k], tools.LIST):
            if all([isinstance(x, tools.SIMPLE) for x in obj]):
                new_obj[k_pre] = tools.join_cr(obj=obj.pop(k), pre=False, indent=None)
                continue

        new_sub_obj = _complex(obj=obj[k], pre=k_pre)
        new_obj.update(new_sub_obj)

        if not obj[k]:
            obj.pop(k)

    return new_obj


def _list_dicts(obj, pre):
    """Pass."""
    new_obj = {}
    for idx, sub_obj in enumerate(list(obj)):
        k_pre = tools.join_dot(obj=[pre, idx])

        new_sub_obj = _complex(obj=sub_obj, pre=k_pre)
        new_obj.update(new_sub_obj)
        if not sub_obj:
            obj.remove(sub_obj)
    return new_obj


def _list_simples(obj, pre):
    """Pass."""
    new_obj = {}
    new_sub_obj = []

    for sub_obj in list(obj):
        new_sub_obj.append(tools.join_cr(obj=sub_obj, pre=False, indent=None))
        obj.remove(sub_obj)

    new_obj[pre] = tools.join_cr(obj=new_sub_obj, pre=False, indent=None)
    return new_obj


def _complex(obj, pre):
    """Pass."""
    if isinstance(obj, dict):
        return _dict(obj=obj, pre=pre)

    if isinstance(obj, list):
        if all([isinstance(x, dict) for x in obj]):
            return _list_dicts(obj=obj, pre=pre)

        if all([isinstance(x, tools.LIST) for x in obj]):
            if all([isinstance(y, tools.SIMPLE) for x in obj for y in x]):
                return _list_simples(obj=obj, pre=pre)

    msg = "Unhandled complex type {t}: {o}"
    msg = msg.format(t=type(obj), o=obj)
    raise exceptions.ToolsError(msg)
