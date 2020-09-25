#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
from __future__ import absolute_import, division, print_function, unicode_literals


def jdump(obj, **kwargs):
    """JSON dump utility."""
    print(axonapi.tools.json_reload(obj, **kwargs))


def get_dvcs_with_cves(dvcs):
    """Get only the devices that have vulnerable sw info."""
    return [x for x in dvcs if x.get("specific_data.data.software_cves")]


def filter_cvss(dvcs, cvss_min, cvss_max):
    """Get only devices with vuln sw with cvss score in between min/max."""
    for dvc in dvcs:
        new_dvc = dvc.copy()
        vuln_sws = dvc.get("specific_data.data.software_cves", [])
        new_dvc["found_vuln"] = []
        for vuln_sw in vuln_sws:
            cvss = vuln_sw.get("cvss", 0.0)
            if cvss_min <= cvss <= cvss_max and vuln_sw not in new_dvc["found_vuln"]:
                new_dvc["found_vuln"].append(vuln_sw)
        if new_dvc["found_vuln"]:
            yield new_dvc


def dump_cves(dvcs, dvc_keys, sw_keys):
    """Report printer."""
    ktmpl = "{s}{k}: {v}".format
    dvcs = [x for x in dvcs if x.get("found_vuln", [])]
    for dvc in dvcs:
        found_vuln = dvc.get("found_vuln", [])
        found_vuln = sorted(found_vuln, key=lambda x: x["cvss"], reverse=True)
        print("*" * 80)
        items = {k: v for k, v in dvc.items() if k in dvc_keys}
        for k, v in items.items():
            print(ktmpl(s=" " * 4, k=k, v=v))
        for sw in found_vuln:
            print("-" * 80)
            sw_items = {k: v for k, v in sw.items() if k in sw_keys}
            for k, v in sw_items.items():
                print(ktmpl(s=" " * 8, k=k, v=v))


if __name__ == "__main__":
    import os

    import axonius_api_client as axonapi

    tools = axonapi.tools
    axonapi.constants.load_dotenv()

    AX_URL = os.environ["AX_URL"]
    AX_KEY = os.environ["AX_KEY"]
    AX_SECRET = os.environ["AX_SECRET"]

    ctx = axonapi.Connect(
        url=AX_URL,
        key=AX_KEY,
        secret=AX_SECRET,
        certwarn=False,
        log_level_console="debug",
        log_level_api="debug",
        log_console=False,
    )

    ctx.start()

    devices = ctx.devices
    users = ctx.users
    adapters = ctx.adapters

    QUERY = None
    FIELDS = ["software_cves"]
    CVSS_MIN = 6.0
    CVSS_MAX = 10.0
    DUMP_DVC_KEYS = [
        "specific_data.data.hostname",
        "specific_data.data.name",
        "specific_data.data.network_interfaces.ips",
        "internal_axon_id",
    ]
    DUMP_SW_KEYS = [
        "cve_id",
        "cve_severity",
        "cvss",
        "software_name",
        "software_vendor",
    ]

    dvcs = devices.get(query=QUERY, fields=FIELDS)

    dvcs_with_cves = get_dvcs_with_cves(dvcs=dvcs)

    dvcs_cvss_minmax = list(filter_cvss(dvcs=dvcs_with_cves, cvss_min=CVSS_MIN, cvss_max=CVSS_MAX))

    dump_cves(dvcs=dvcs_cvss_minmax, dvc_keys=DUMP_DVC_KEYS, sw_keys=DUMP_SW_KEYS)
