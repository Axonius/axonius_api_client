# -*- coding: utf-8 -*-
"""API models for working with adapters and connections."""
import copy
import textwrap
from typing import List, Optional, Union

import tabulate

from ...constants import KEY_MAP_ADAPTER, KEY_MAP_CNX, KEY_MAP_SCHEMA
from ...tools import json_dump


def tablize(
    value: List[dict],
    err: Optional[str] = None,
    fmt: str = "simple",
    footer: bool = True,
    **kwargs
) -> str:
    """Pass."""
    # value = wrapper(value=value, **kwargs)

    table = tabulate.tabulate(value, tablefmt=fmt, headers="keys")

    if footer:
        if fmt == "simple":
            header = "\n" + "\n".join(reversed(table.splitlines()[0:2]))
            table += header

    if err:
        pre = err + "\n"
        post = "\n" + err
    else:
        pre = "\n"
        post = "\n"

    return "\n".join([pre, table, post])


def tablize_schemas(
    schemas: List[dict],
    config: Optional[dict] = None,
    err: Optional[str] = None,
    fmt: str = "simple",
    footer: bool = True,
    orig: bool = True,
    orig_width: int = 20,
) -> str:
    """Pass."""
    values = []
    config = config or None
    if isinstance(schemas, dict):
        schemas = list(schemas.values())

    # XXX TRANSLATE ENUM DICTS!!
    for schema in sorted(schemas, key=lambda x: [x["required"], x["name"]]):
        value = tab_map(
            value=schema, key_map=KEY_MAP_SCHEMA, orig=orig, orig_width=orig_width
        )
        if config:
            config_value = config.get(schema["name"], None)
            if isinstance(config_value, dict):
                config_value = json_dump(config_value)
            value["Current Value"] = config_value
        values.append(value)

    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tablize_adapters(
    adapters: List[dict],
    err: Optional[str] = None,
    fmt: str = "simple",
    footer: bool = True,
) -> str:
    """Pass."""
    values = []

    for adapter in adapters:
        value = tab_map(value=adapter, key_map=KEY_MAP_ADAPTER, orig=False)
        # value["Connection IDs"] = "\n".join([x["id"] for x in adapter["cnx"]])
        values.append(value)

    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tablize_cnxs(
    cnxs: List[dict], err: Optional[str] = None, fmt: str = "simple", footer: bool = True
) -> str:
    """Pass."""
    values = []
    for cnx in cnxs:
        cnx["label"] = cnx["config"].get("connection_label")
        value = tab_map(value=cnx, key_map=KEY_MAP_CNX, orig=False)
        values.append(value)

    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tab_map(
    value: dict,
    key_map: List[List[Union[str, str, int]]],
    orig: bool = False,
    orig_width: int = 20,
) -> str:
    """Pass."""
    orig_value = copy.deepcopy(value)

    new_value = {}

    for key, name, width in key_map:
        if key in orig_value and name:

            key_value = orig_value.pop(key)

            if isinstance(key_value, list):
                key_value = "\n".join([str(x) for x in key_value])

            if isinstance(key_value, str) and key_value and width:
                key_value = textwrap.fill(key_value, width=width)

            new_value[name] = key_value

    if orig:
        for orig_key, orig_key_value in orig_value.items():
            if isinstance(orig_key_value, dict):
                continue

            if isinstance(orig_key_value, list):
                new_value[orig_key] = "\n".join([str(x) for x in orig_key_value])

            elif isinstance(orig_key_value, str) and orig_key_value and orig_width:
                new_value[orig_key] = textwrap.fill(orig_key_value, width=orig_width)
            else:
                new_value[orig_key] = orig_key_value

    return new_value
