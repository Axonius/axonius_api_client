#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import os

import axonius_api_client as axonapi

if __name__ == "__main__":
    axonapi.constants.load_dotenv()

    AX_URL = os.environ["AX_URL"]
    AX_KEY = os.environ["AX_KEY"]
    AX_SECRET = os.environ["AX_SECRET"]
    AX_CLIENT_CERT_BOTH = os.environ.get("AX_CLIENT_CERT_BOTH", None) or None
    AX_CLIENT_CERT_CERT = os.environ.get("AX_CLIENT_CERT_CERT", None) or None
    AX_CLIENT_CERT_KEY = os.environ.get("AX_CLIENT_CERT_KEY", None) or None

    def jdump(obj, **kwargs):
        """JSON dump utility."""
        print(axonapi.tools.json_reload(obj, **kwargs))

    ctx = axonapi.Connect(
        url=AX_URL,
        key=AX_KEY,
        secret=AX_SECRET,
        certwarn=False,
        cert_client_both=AX_CLIENT_CERT_BOTH,
        cert_client_cert=AX_CLIENT_CERT_CERT,
        cert_client_key=AX_CLIENT_CERT_KEY,
        log_level_console="debug",
        log_level_api="debug",
        log_level_http="debug",
        # log_request_attrs=["url", "size", "method"],
        # log_response_attrs=["status", "size"],
        # log_request_body=True,
        # log_response_body=True,
        # log_console=True,
    )

    ctx.start()
    devices = ctx.devices
    users = ctx.users
    adapters = ctx.adapters
    enforcements = ctx.enforcements
    system = ctx.system

    query = '(((specific_data.data.installed_software == ({"$exists":true,"$ne":[]})) and specific_data.data.installed_software != []))'  # noqa
    fields = ["installed_software"]
    whitelist = [
        "Symantec CMC Firewall",
        "Symantec Client Management Component",
        "Symantec Core Technology",
        "Symantec Endpoint Protection",
        "Symantec Install Component",
        "Symantec Network Access Control",
        "Symantec Security Drivers",
        "Symantec Security Technologies",
        "Symantec Shared Component",
        "kaseya",
        "chrome",
        "boogey-boogey",
    ]

    assets = devices.get(
        query=query,
        fields=fields,
        max_rows=1,
        report_software_whitelist=whitelist,
        export="csv",
        export_file="blah.csv",
        export_overwrite=True,
    )
