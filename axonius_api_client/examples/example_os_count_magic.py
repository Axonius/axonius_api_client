#!/usr/bin/env python -i
# -*- coding: utf-8 -*-
"""Example of getting all OS types and post-processing for missing build versions."""
import csv
import json  # noqa: F401
import os
import pathlib
import re

import axonius_api_client as axonapi  # noqa: F401
from axonius_api_client.connect import Connect
from axonius_api_client.tools import json_reload, listify

FIELDS = [
    "os.type",
    "os.distribution",
    "os.build",
    "os.os_str",
]

BITS_MAPS = {
    "os.type_preferred": "type",
    "os.distribution_preferred": "dist",
    "os.os_str_preferred": "str",
    "os.build_preferred": "build",
}


SEARCH_MAPS = [
    {
        "searches": {"str": re.compile(r"cisco.*unified communications manager", re.I)},
        "updates": {"dist": "Unified Communications Manager"},
    },
    {
        "searches": {"str": re.compile(r"cisco.*catalyst", re.I)},
        "updates": {"dist": "Catalyst"},
    },
    {
        "searches": {"str": re.compile(r"^catalyst", re.I)},
        "updates": {"dist": "Catalyst"},
    },
    {
        "searches": {"dist": re.compile(r"vmware esxi (.*)", re.DOTALL | re.I)},
        "updates": {"dist": "ESXi", "build": 0},
        "overwrites": ["dist", "build"],
    },
    {
        "searches": {"str": re.compile(r"cisco.*linux release:([\d.\-]+)", re.I)},
        "updates": {"build": 0},
    },
    {
        "searches": {"str": re.compile(r"other ([\d.x]+) linux", re.I)},
        "updates": {"build": 0},
    },
    {
        "searches": {"str": re.compile(r"software:ucos ([\d.\-di]+)", re.I)},
        "updates": {"build": 0},
    },
    {
        "searches": {"str": re.compile(r"cisco.* \((.*?)\), version ([\d.\w, \(\)]+)", re.I)},
        "updates": {"build": 1, "dist": 0},
    },
    {
        "searches": {"str": re.compile(r"cisco.*\nsoftw: ([\w\d.]+)", re.I)},
        "updates": {"build": 0},
    },
    {
        "searches": {"str": re.compile(r"check point.*linux.*? (\d[\d.\w\-]+) ", re.I)},
        "updates": {"build": 0, "dist": "Check Point"},
    },
    {
        "searches": {"str": re.compile(r"net-snmp.*? (\d[\d.\-\w]+) ", re.I)},
        "updates": {"build": 0, "dist": "net-snmp", "type": "Linux"},
        "overwrites": ["type"],
    },
    {
        "searches": {"str": re.compile(r"big-ip software release (.*)", re.DOTALL | re.I)},
        "updates": {"build": 0, "dist": "Big-IP"},
    },
    {
        "searches": {"str": re.compile(r"eaton.*v(.*)", re.DOTALL | re.I)},
        "updates": {"build": 0},
    },
    {
        "searches": {"str": re.compile(r"cisco (airct.*) cisco controller", re.I)},
        "updates": {"build": 0},
    },
    {
        "searches": {"str": re.compile(r"adtran.*version: ([\d.\w]+), ", re.I)},
        "updates": {"build": 0},
    },
    {
        "searches": {"str": re.compile(r"adtran.*rev. ([\d.\w]+)", re.DOTALL | re.I)},
        "updates": {"build": 0},
    },
    {
        "searches": {"str": re.compile(r"(japan computer.*?) (\d[\d.\w\-]+) ", re.DOTALL | re.I)},
        "updates": {"build": 1, "dist": 0},
    },
    {
        "searches": {"str": re.compile(r"matsushita.*swver(\d[\d.]+)", re.DOTALL | re.I)},
        "updates": {"build": 0},
    },
    {
        "searches": {"str": re.compile("sles", re.I)},
        "updates": {"type": "Linux", "dist": "SuSe Linux"},
    },
    {
        "searches": {"str": re.compile("windows_10", re.I)},
        "updates": {"type": "Windows", "dist": "10"},
    },
    {
        "searches": {"str": re.compile("windows_7", re.I)},
        "updates": {"type": "Windows", "dist": "7"},
    },
    {
        "searches": {"str": re.compile("windows_98", re.I)},
        "updates": {"type": "Windows", "dist": "98"},
    },
    {
        "searches": {"str": re.compile("windows_2000", re.I)},
        "updates": {"type": "Windows", "dist": "2000"},
    },
    {"searches": {"str": re.compile("linux", re.I)}, "updates": {"type": "Linux"}},
    {"searches": {"str": re.compile("os x", re.I)}, "updates": {"type": "OS X"}},
    {"searches": {"str": re.compile("cisco", re.I)}, "updates": {"type": "Cisco"}},
    {"searches": {"str": re.compile("ios", re.I)}, "updates": {"type": "iOS"}},
    {"searches": {"str": re.compile("airos", re.I)}, "updates": {"type": "AirOS"}},
    {"searches": {"str": re.compile("android", re.I)}, "updates": {"type": "Android"}},
    {"searches": {"str": re.compile("freebsd", re.I)}, "updates": {"type": "FreeBSD"}},
    {"searches": {"str": re.compile("vmware", re.I)}, "updates": {"type": "VMWare"}},
    {"searches": {"str": re.compile("mikrotik", re.I)}, "updates": {"type": "Mikrotik"}},
    {"searches": {"str": re.compile("vxworks", re.I)}, "updates": {"type": "VxWorks"}},
    {"searches": {"str": re.compile("panos", re.I)}, "updates": {"type": "PanOS"}},
    {
        "searches": {"str": re.compile("big-ip", re.I)},
        "updates": {"type": "F5 Networks Big-IP"},
    },
    {"searches": {"str": re.compile("solaris", re.I)}, "updates": {"type": "Solaris"}},
    {"searches": {"str": re.compile("aix", re.I)}, "updates": {"type": "AIX"}},
    {"searches": {"str": re.compile("printer", re.I)}, "updates": {"type": "Printer"}},
    {
        "searches": {"str": re.compile("playstation", re.I)},
        "updates": {"type": "PlayStation"},
    },
    {
        "searches": {"str": re.compile("check point", re.I)},
        "updates": {"type": "Check Point"},
    },
    {"searches": {"str": re.compile("arista", re.I)}, "updates": {"type": "Arista"}},
    {
        "searches": {"str": re.compile("netscaler", re.I)},
        "updates": {"type": "Netscaler"},
    },
    {
        "searches": {"str": re.compile("meraki mx250", re.I)},
        "updates": {"type": "Meraki", "dist": "mx250"},
    },
    {
        "searches": {"str": re.compile("integrated_lights-out", re.I)},
        "updates": {"type": "HP iLO"},
    },
    {
        "searches": {"str": re.compile("cisco cgs-2520-16s-8pc", re.I)},
        "updates": {"dist": "cgs-2520-16s-8pc"},
    },
    {
        "searches": {"str": re.compile("cisco cgs-2520-24tc", re.I)},
        "updates": {"dist": "cgs-2520-24tc"},
    },
    {
        "searches": {"str": re.compile("cisco ws-c3560v2-48ps", re.I)},
        "updates": {"dist": "ws-c3560v2-48ps"},
    },
    {
        "searches": {"str": re.compile("vg3x0 software", re.I)},
        "updates": {"dist": "VG3X0 Analog Voice Gateway"},
    },
    {
        "searches": {"str": re.compile(r"network_camera_firmware.*axis", re.I | re.DOTALL)},
        "updates": {"dist": "Axis network camera firmware"},
    },
]


def get_value(asset: dict, field: str, pre: str = "specific_data.data"):
    value = listify(asset.get(f"{pre}.{field}", []))
    value = sorted(list(set([x for x in value if x])))
    if len(value) == 0:
        return ""
    if len(value) == 1:
        return value[0]
    return value


def get_bits(asset: dict):
    value = {v: get_value(asset=asset, field=k) for k, v in BITS_MAPS.items()}
    return value


def empty_dist_type(bits):
    logs = []
    src = bits["str"]
    key1 = "dist"
    key2 = "type"
    value1 = bits[key1]
    value2 = bits[key2]
    if src and not value1 and not value2:
        log = {
            "action": f"empty {key1!r} and empty {key2!r}",
            "update_key": key1,
            "update_value": src,
        }
        logs.append(log)
        bits[key1] = src
    return logs


def fixup_bits(bits: dict):
    logs = []
    logs += search_maps(bits)
    logs += empty_dist_type(bits)
    logs += switch_dist_build(bits)
    return logs


def switch_dist_build(bits):
    logs = []
    types = ["iOS", "Android"]
    # just check if dist is a "version" and build is empty
    if bits["type"] in types and not bits["build"] and bits["dist"]:
        bits["build"] = bits["dist"]
        bits["dist"] = ""
    return logs


def search_maps(bits):
    logs = []
    for search_map in SEARCH_MAPS:
        searches = search_map["searches"]
        updates = search_map.get("updates", {})
        overwrites = search_map.get("overwrites", [])

        for search_key, search_re in searches.items():
            search_value = bits[search_key]
            pattern = search_re.pattern
            match = search_re.search(search_value)

            if not match:
                continue

            for key, value in updates.items():
                if isinstance(value, int):
                    value = match.groups()[value].strip(".").strip()

                bits_value = bits[key]
                log = {
                    "action": f"set empty key {key!r} to value {value!r}",
                    "original_value": bits_value,
                    "update_key": key,
                    "update_value": value,
                    "search_pattern": pattern,
                    "search_key": search_key,
                    "search_value": search_value,
                }
                if not bits_value:
                    log["action"] = "set empty key"
                    logs.append(log)
                    bits[key] = value
                elif key in overwrites:
                    log["action"] = "overwrote key"
                    logs.append(log)
                    bits[key] = value
    return logs


def get_assets(apiobj):
    pref_fields = [f"{x}_preferred" for x in FIELDS]
    assets = devices.get(fields=FIELDS + pref_fields)
    # fh = open("/tmp/allete.json")
    # assets = json.load(fh)
    print(f"Fetched {len(assets)} assets")
    return assets


def parse_assets(assets):
    results = {}
    for asset in assets:
        bits = get_bits(asset=asset)
        logs = fixup_bits(bits=bits)

        _ = bits.pop("str")
        str_bits = str(bits)

        if str_bits not in results:
            results[str_bits] = bits
            results[str_bits]["count"] = 0
            results[str_bits]["logs"] = []

        for log in logs:
            if log not in results[str_bits]["logs"]:
                results[str_bits]["logs"].append(log)

        results[str_bits]["count"] += 1

    return sorted(
        list(results.values()),
        key=lambda x: [x["type"], x["dist"], x["build"], x["count"]],
    )


def write_csv(results, path="os_counts.csv", logs=True):
    path = pathlib.Path(path)
    fields = list(results[0].keys())
    if not logs:
        fields = [x for x in fields if x != "logs"]
    with path.open("w") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", quoting=csv.QUOTE_ALL)
        writer.writerow(dict(zip(fields, fields)))
        for result in results:
            for k, v in result.items():
                if isinstance(v, list):
                    result[k] = "  - " + "\n  - ".join([str(x) for x in v])
            writer.writerow(result)
    print(f"wrote results to {path}")


def jdump(obj, **kwargs):
    """JSON dump utility."""
    print(json_reload(obj, **kwargs))


j = jdump

if __name__ == "__main__":
    AX_URL = os.environ["AX_URL"]
    AX_KEY = os.environ["AX_KEY"]
    AX_SECRET = os.environ["AX_SECRET"]
    ctx = Connect(url=AX_URL, key=AX_KEY, secret=AX_SECRET, certwarn=False)
    ctx.start()
    devices = ctx.devices

    assets = get_assets(devices)
    results = parse_assets(assets)
    write_csv(results)
