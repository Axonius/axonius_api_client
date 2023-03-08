# -*- coding: utf-8 -*-
"""Parsers for tables."""
import copy
import textwrap
from typing import List, Optional, Union

import tabulate

from ..constants.api import TABLE_FORMAT
from ..constants.tables import KEY_MAP_ADAPTER, KEY_MAP_SCHEMA
from ..tools import json_dump, listify


def tablize(
    value: List[dict],
    err: Optional[str] = None,
    fmt: str = TABLE_FORMAT,
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
    use_footer = ""

    if footer:
        if fmt in ["simple", "grid"]:
            use_footer = "\n".join(reversed(table.splitlines()[0:2]))

    if err:
        pre = err + "\n"
        post = "\n" + err
    else:
        pre = "\n"
        post = "\n"

    return "\n".join([x for x in [pre, table, use_footer, post] if x])


def tablize_schemas(
    schemas: List[dict],
    config: Optional[dict] = None,
    err: Optional[str] = None,
    fmt: str = TABLE_FORMAT,
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
    fmt: str = TABLE_FORMAT,
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
    cnxs: List[dict], err: Optional[str] = None, fmt: str = TABLE_FORMAT, footer: bool = True
) -> str:
    """Create a table string for a set of adapter connection schemas.

    Args:
        cnxs: connection schemas to create a table from
        err: error string to show at top
        fmt: table format to use
        footer: show err at bottom too
    """
    """
    old key map: [
        ("id", "ID", 0),
        ("uuid", "UUID", 0),
        ("working", "Working", 0),
        ("active", "Active", 0),
        ("connection_label", "Label", 0),
        ("schemas", None, 0),
    ]
    """

    def join(obj):
        return "\n".join(obj)

    def config_str(k, v):
        ret = f"{k} ({type(v).__name__}): {v}"
        return ret

    def schema_str(obj):
        req = "REQUIRED, " if obj["required"] else ""
        return "{name} ({req}{type})".format(req=req, **obj)

    def get_value(cnx):
        error = textwrap.fill(cnx["error"] or "", width=30, subsequent_indent=" " * 2)
        details = [
            f'Adapter: {cnx["adapter_name"]}',
            f'Node Name: {cnx["node_name"]}',
            f'Node ID: {cnx["node_id"]}',
            f'Tunnel ID: {cnx["tunnel_id"]}',
            f'ID: {cnx["id"]}',
            f'UUID: {cnx["uuid"]}',
            f'Label: {cnx["connection_label"]}',
            f'Active: {cnx["active"]}',
            f'Working: {cnx["working"]}',
            f"Error: {error}",
        ]
        configs = [config_str(k, v) for k, v in sorted(cnx["config"].items())]

        value = {}
        value["Details"] = join(details)
        value["Config"] = join(configs)
        return value

    values = [get_value(cnx) for cnx in cnxs]

    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tablize_sqs(data: List[dict], err: str, fmt: str = TABLE_FORMAT, footer: bool = True) -> str:
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
    if callable(getattr(data, "to_tablize", None)):
        return data.to_tablize()

    data = data.to_dict() if hasattr(data, "to_dict") else data

    name = data["name"]
    # name = textwrap.fill(name, width=40, subsequent_indent=" " * 2)
    uuid = data["uuid"]
    description = data.get("description") or ""
    description = textwrap.fill(description, width=30)
    tags = listify(data.get("tags"))
    tags = "\n  " + "\n  ".join(tags)
    updated = data.get("last_updated")

    flags = {
        "is predefined": data.get("predefined", False),
        "is referenced": data.get("is_referenced", False),
        "is private": data.get("private", False),
        "is always cached": data.get("always_cached", False),
        "is asset scope": data.get("asset_scope", False),
        "is asset scope ready": data.get("is_asset_scope_query_ready", False),
    }
    flags = "\n".join([f"{k}: {v}" for k, v in flags.items()])

    details = [
        f"Name: {name}",
        f"UUID: {uuid}",
        f"Updated: {updated}",
        f"Tags: {tags}",
    ]
    value = {}
    value["Details"] = "\n".join(details)
    value["Description"] = description
    value["Flags"] = flags
    return value


def tablize_users(users: List[dict], err: str, fmt: str = TABLE_FORMAT, footer: bool = True) -> str:
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


def tablize_roles(roles: List[dict], err: str, fmt: str = TABLE_FORMAT, footer: bool = True) -> str:
    """Create a table string for a set of roles.

    Args:
        roles: roles to create a table from
        err: error string to show at top
        fmt: table format to use
        footer: show err at bottom too
    """
    values = [tablize_role(role=x) for x in roles]
    return tablize(value=values, err=err, fmt=fmt, footer=footer)


def tablize_role(role: dict) -> dict:
    """Create a table entry for a role.

    Args:
        role: role to create a table entry for
    """
    name = role["name"]
    uuid = role["uuid"]
    perms = role["permissions_flat"]
    updated = role.get("last_updated")
    predefined = role.get("predefined", False)
    users_count = role.get("users_count")
    dsr = role.get("data_scope_restriction") or {}

    value_perms = []
    for cat, action in perms.items():
        if all(list(action.values())):
            has_perms = "all"
        elif all([v is False for k, v in action.items()]):
            has_perms = "none"
        else:
            has_perms = "\n  ".join([k for k, v in action.items() if v])
        value_perms.append(f"{cat}:\n  {has_perms}")

    value_perms = "\n".join(value_perms)

    dsr_name = role.get("data_scope_name")
    data_scope = [f"{k}: {v!r}" for k, v in dsr.items()] + [f"Name: {dsr_name!r}"]

    details = [
        f"Name: {name}",
        f"UUID: {uuid}",
        f"Updated: {updated}",
        f"Users Count: {users_count}",
        f"Predefined: {predefined}",
    ]

    value = {}
    value["Details"] = "\n".join(details)
    value["Permissions"] = value_perms
    value["Data Scope"] = "\n".join(data_scope)
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
