# -*- coding: utf-8 -*-
"""API models for working with adapters and connections."""
from typing import List

from ...constants import DISCOVERY_NAME, GENERIC_NAME
from ...tools import strip_right
from .config import parse_schema


def parse_adapters(raw: dict) -> List[dict]:
    """Parser to turn adapters metadata into a more friendly format."""
    parsed = []

    for name, raws in raw.items():
        for raw in raws:
            adapter = parse_adapter(name=name, raw=raw)
            parsed.append(adapter)

    return parsed


def parse_adapter(name: str, raw: dict) -> dict:
    """Parse a single adapter."""
    parsed = {
        "name": strip_right(obj=name, fix="_adapter"),
        "name_raw": name,
        "name_plugin": raw.get("unique_plugin_name", f"{name}_0"),
        # XXX REMOVE POST 3.5, should be direct reference, no more get
        "node_name": raw["node_name"],
        "node_id": raw["node_id"],
        "status": raw["status"],
        "features": raw["supported_features"],
    }

    generic_name = GENERIC_NAME
    discovery_name = DISCOVERY_NAME

    specific_name = get_specific_name(raw=raw)
    config = raw["config"]

    specific_schema = config.get(specific_name, {}).get("schema", {})
    specific_schema = parse_schema(raw=specific_schema)

    generic_schema = config[generic_name]["schema"]
    generic_schema = parse_schema(raw=generic_schema)

    discovery_schema = config[discovery_name]["schema"]
    discovery_schema = parse_schema(raw=discovery_schema)

    cnx_schema = parse_schema(raw=raw["schema"])
    cnx_schema["connection_label"] = {
        "name": "connection_label",
        "title": "Connection Label",
        "type": "string",
        "required": False,
    }

    parsed["schemas"] = {
        "cnx": cnx_schema,
        "specific": specific_schema,
        "generic": generic_schema,
        "discovery": discovery_schema,
        "generic_name": generic_name,
        "specific_name": specific_name,
        "discovery_name": discovery_name,
    }

    parsed["config"] = {
        "specific": raw["config"].get(specific_name, {}).get("config", {}),
        "generic": raw["config"].get(generic_name, {}).get("config", {}),
        "discovery": raw["config"].get(discovery_name, {}).get("config", {}),
    }

    parsed["cnx"] = parse_cnx(raw=raw, parsed=parsed)
    parsed["cnx_count_total"] = len(parsed["cnx"])
    parsed["cnx_count_broken"] = len([x for x in parsed["cnx"] if not x["working"]])
    parsed["cnx_count_working"] = len([x for x in parsed["cnx"] if x["working"]])

    return parsed


def get_specific_name(raw: dict) -> str:
    """Pass."""
    found = [x for x in raw["config"] if x not in [GENERIC_NAME, DISCOVERY_NAME]]
    return found[0] if found else ""


def parse_cnx(raw: dict, parsed: dict) -> List[dict]:
    """Parse the connection metadata for this adapter."""
    cnx = []

    for cnx_raw in raw["clients"]:
        cnx_parsed = {}
        cnx_parsed["config"] = cnx_raw["client_config"]
        cnx_parsed["adapter_name"] = parsed["name"]
        cnx_parsed["adapter_name_raw"] = parsed["name_raw"]
        cnx_parsed["node_name"] = parsed["node_name"]
        cnx_parsed["node_id"] = parsed["node_id"]
        cnx_parsed["status"] = cnx_raw["status"]
        cnx_parsed["working"] = cnx_raw["status"] == "success" and not cnx_raw["error"]
        cnx_parsed["id"] = cnx_raw["client_id"]
        cnx_parsed["uuid"] = cnx_raw["uuid"]
        cnx_parsed["date_fetched"] = cnx_raw["date_fetched"]
        cnx_parsed["error"] = cnx_raw["error"]
        cnx.append(cnx_parsed)

    return cnx
