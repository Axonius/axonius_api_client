# -*- coding: utf-8 -*-
"""Parsers for adapter schemas."""
import copy
from typing import List

from ..constants.adapters import DISCOVERY_NAME, GENERIC_NAME
from ..tools import strip_right
from .config import parse_schema

# from .. import json_api


CNX_LABEL_SCHEMA = {
    "name": "connection_label",
    "title": "Connection Label",
    "type": "string",
    "required": False,
}


def parse_adapters(raw: List[dict]) -> List[dict]:
    """Parser to turn adapters metadata into a more friendly format.

    Args:
        raw: the raw output from :meth:`axonius_api_client.api.adapters.adapters.Adapters._get`
    """
    parsed = []
    for adapter_obj in raw:
        adapter = adapter_obj.to_dict()
    for name, adapters in raw.items():
        for adapter in adapters:
            adapter = parse_adapter(name=name, adapter=adapter)
            parsed.append(adapter)
    return parsed


def parse_adapter(name: str, adapter: dict) -> dict:
    """Parse a single adapter.

    Args:
        name: raw name of adapter (aws_adapter)
        adapter: adapter meta data
    """
    adapter = copy.deepcopy(adapter)
    unique_plugin_name = adapter.pop("unique_plugin_name")
    node_name = adapter.pop("node_name")
    node_id = adapter.pop("node_id")
    status = adapter.pop("status")
    supported_features = adapter.pop("supported_features")
    config = adapter.get("config", {})
    cnxs = adapter.pop("clients")
    cnx_schema = adapter.pop("schema")

    cnx_schema = parse_schema(raw=cnx_schema)
    # FYI old hack, may not be needed anymore
    cnx_schema["connection_label"] = cnx_schema.get("connection_label", CNX_LABEL_SCHEMA)

    adapter["name"] = strip_right(obj=name, fix="_adapter")
    adapter["name_raw"] = name
    adapter["name_plugin"] = unique_plugin_name
    adapter["node_name"] = node_name
    adapter["node_id"] = node_id
    adapter["status"] = status
    adapter["features"] = supported_features
    adapter["schemas"] = {"cnx": cnx_schema}
    adapter["config"] = {}

    advanced_schema_names = {
        "generic": GENERIC_NAME,
        "discovery": DISCOVERY_NAME,
        "specific": get_specific_name(config=config),
    }

    for adv_key, adv_name in advanced_schema_names.items():
        adv_root = config.get(adv_name, {})
        adv_schema = adv_root.pop("schema", {})
        adv_config = adv_root.pop("config", {})
        adapter["schemas"][f"{adv_key}_name"] = adv_name
        adapter["schemas"][adv_key] = parse_schema(raw=adv_schema)
        adapter["config"][adv_key] = adv_config

    adapter["cnx"] = parse_cnxs(cnxs=cnxs, adapter=adapter)
    adapter["cnx_count_total"] = len(adapter["cnx"])
    adapter["cnx_count_broken"] = len([x for x in adapter["cnx"] if not x["working"]])
    adapter["cnx_count_working"] = len([x for x in adapter["cnx"] if x["working"]])

    return adapter


def get_specific_name(config: dict) -> str:
    """Get the name of the specific schema for the current adapter.

    Args:
        config: advanced settings schemas for current adapter
    """
    found = [x for x in config if x not in [GENERIC_NAME, DISCOVERY_NAME]]
    return found[0] if found else ""


def parse_cnxs(cnxs: List[dict], adapter: dict) -> List[dict]:
    """Parse the connections metadata for this adapter.

    Args:
        cnxs: connections of current adapter
        adapter: current adapter metadata
    """
    return [parse_cnx(cnx=x, adapter=adapter) for x in cnxs]


def parse_cnx(cnx: dict, adapter: dict) -> List[dict]:
    """Parse the connection metadata for this adapter.

    Args:
        cnx: current connection
        adapter: current adapter metadata
    """
    status = cnx.pop("status")
    error = cnx.pop("error")
    client_config = cnx.pop("client_config")
    client_id = cnx.pop("client_id")
    uuid = cnx.pop("uuid")
    date_fetched = cnx.pop("date_fetched")

    # FYI gone 3.10 ??
    error = cnx.pop("error", "")

    cnx["config"] = client_config
    cnx["adapter_name"] = adapter["name"]
    cnx["adapter_name_raw"] = adapter["name_raw"]
    cnx["node_name"] = adapter["node_name"]
    cnx["node_id"] = adapter["node_id"]
    cnx["status"] = status
    cnx["working"] = status == "success" and not error
    cnx["id"] = client_id
    cnx["uuid"] = uuid
    cnx["date_fetched"] = date_fetched
    cnx["error"] = error
    return cnx
