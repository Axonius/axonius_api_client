# -*- coding: utf-8 -*-
"""Parsers for tables."""
import copy
import textwrap
from typing import List, Optional, Union

import tabulate

from ..constants.tables import KEY_MAP_ADAPTER, KEY_MAP_CNX, KEY_MAP_SCHEMA, TABLE_FMT
from ..tools import json_dump, listify


def tablize(
    value: List[dict],
    err: Optional[str] = None,
    fmt: str = TABLE_FMT,
    footer: bool = True,
    **kwargs,
) -> str:
    """Create a table string from a list of dictionaries.

    Args:
        value: list to create table from
        err: error string to display at top of table
        fmt: table format to use
        footer: include err at bottom too
    """
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
    fmt: str = TABLE_FMT,
    footer: bool = True,
    orig: bool = True,
    orig_width: int = 20,
) -> str:
    """Create a table string for a set of config schemas.

    Args:
        schemas: config schemas to create a table from
        config: current config with keys that map to schema names
        err: error string to show at top
        fmt: table format to use
        footer: show err at bottom too
        orig: show original values in output too
        orig_width: column width to use for orig values
    """
    values = []
    config = config or None
    if isinstance(schemas, dict):
        schemas = list(schemas.values())

    # TBD TRANSLATE ENUM DICTS!!
    for schema in sorted(schemas, key=lambda x: [x["required"], x["name"]]):
        value = tab_map(value=schema, key_map=KEY_MAP_SCHEMA, orig=orig, orig_width=orig_width)
        if config:
            config_value = config.get(schema["name"], None)
            if isinstance(config_value, dict):  # pragma: no cover
                config_value = json_dump(config_value)
            value["Current Value"] = config_value
        values.append(value)

    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tablize_adapters(
    adapters: List[dict],
    err: Optional[str] = None,
    fmt: str = TABLE_FMT,
    footer: bool = True,
) -> str:
    """Create a table string for a set of adapter schemas.

    Args:
        adapters: adapter schemas to create a table from
        err: error string to show at top
        fmt: table format to use
        footer: show err at bottom too
    """
    values = []

    for adapter in adapters:
        value = tab_map(value=adapter, key_map=KEY_MAP_ADAPTER, orig=False)
        # value["Connection IDs"] = "\n".join([x["id"] for x in adapter["cnx"]])
        values.append(value)

    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tablize_cnxs(
    cnxs: List[dict], err: Optional[str] = None, fmt: str = TABLE_FMT, footer: bool = True
) -> str:
    """Create a table string for a set of adapter connection schemas.

    Args:
        cnxs: connection schemas to create a table from
        err: error string to show at top
        fmt: table format to use
        footer: show err at bottom too
    """
    values = []
    for cnx in cnxs:
        value = tab_map(value=cnx, key_map=KEY_MAP_CNX, orig=False)
        values.append(value)

    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tablize_sqs(data: List[dict], err: str, fmt: str = TABLE_FMT, footer: bool = True) -> str:
    """Create a table string for a set of sqs.

    Args:
        data: sqs to create a table from
        err: error string to show at top
        fmt: table format to use
        footer: show err at bottom too
    """
    values = [tablize_sq(x) for x in data]
    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tablize_sq(data: dict) -> dict:
    """Create a table entry for a sq.

    Args:
        data: sq to create a table entry for
    """
    value = {}
    value["Name"] = data["name"]  # textwrap.fill(data["name"], width=30)
    value["UUID"] = data["uuid"]
    value["Description"] = textwrap.fill(data.get("description") or "", width=30)
    value["Tags"] = "\n".join(listify(data.get("tags", [])))
    return value


def tablize_users(users: List[dict], err: str, fmt: str = TABLE_FMT, footer: bool = True) -> str:
    """Create a table string for a set of users.

    Args:
        users: users to create a table from
        err: error string to show at top
        fmt: table format to use
        footer: show err at bottom too
    """
    values = [tablize_user(user=x) for x in users]
    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tablize_user(user: dict) -> dict:
    """Create a table entry for a user.

    Args:
        user: user to create a table entry for
    """
    tab_map = {
        "Name": "user_name",
        "UUID": "uuid",
        "Full Name": "full_name",
        "Role Name": "role_name",
        "Email": "email",
        "Last Login": "last_login",
        "Source": "source",
    }
    value = {k: user.get(v) for k, v in tab_map.items()}
    return value


def tablize_roles(
    roles: List[dict], cat_actions: dict, err: str, fmt: str = TABLE_FMT, footer: bool = True
) -> str:
    """Create a table string for a set of roles.

    Args:
        roles: roles to create a table from
        cat_actions: category -> actions mapping
        err: error string to show at top
        fmt: table format to use
        footer: show err at bottom too
    """
    values = [tablize_role(role=x, cat_actions=cat_actions) for x in roles]
    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tablize_role(role: dict, cat_actions: dict) -> dict:
    """Create a table entry for a role.

    Args:
        role: role to create a table entry for
        cat_actions: category -> actions mapping
    """
    tab_map = {"Name": "name", "UUID": "uuid"}
    value = {k: role.get(v) for k, v in tab_map.items()}

    perms = role["permissions_flat"]
    value_perms = []
    for cat, action in perms.items():
        if all(list(action.values())):
            has_perms = "all"
        else:
            has_perms = ", ".join([k for k, v in action.items() if v])
        value_perms.append(f"{cat}: {has_perms}")

    value_perms = "\n".join(value_perms)
    value["Categories: actions"] = value_perms
    return value


def tab_map(
    value: dict,
    key_map: List[List[Union[str, str, int]]],
    orig: bool = False,
    orig_width: int = 20,
) -> dict:
    """Create a new schema that has columns in a table friendly output format.

    Args:
        value: schema to parse
        key_map: key map containing key name -> column title -> column width
        orig: include values from original schema not in key map
        orig_width: default column width to use for values from original schema
    """
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
            if isinstance(orig_key_value, dict):  # pragma: no cover
                continue

            new_key_value = orig_key_value

            if isinstance(orig_key_value, list):
                new_key_value = "\n".join([str(x) for x in orig_key_value])

            if isinstance(orig_key_value, str) and orig_key_value and orig_width:
                new_key_value = textwrap.fill(orig_key_value, width=orig_width)

            new_value[orig_key] = new_key_value

    return new_value
