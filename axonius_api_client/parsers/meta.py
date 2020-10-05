# -*- coding: utf-8 -*-
"""Parsers for product metadata."""
from ..tools import calc_gb


def parse_sizes(raw: dict) -> dict:
    """Parse the disk usage metadata."""
    parsed = {}
    parsed["disk_free_mb"] = calc_gb(value=raw["disk_free"], is_kb=False)
    parsed["disk_used_mb"] = calc_gb(value=raw["disk_used"], is_kb=False)
    parsed["historical_sizes_devices"] = raw["entity_sizes"].get("Devices", {})
    parsed["historical_sizes_users"] = raw["entity_sizes"].get("Users", {})
    return parsed
