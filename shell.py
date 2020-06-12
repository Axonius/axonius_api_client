#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
# import dataclasses
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
    import datetime
    import json

    # field = 'specific_data.data.plugin_and_severities'
    query = '(((specific_data.data.plugin_and_severities == ({"$exists":true,"$ne":[]})) and specific_data.data.plugin_and_severities != []))'  # noqa
    query = None
    # get_fields = devices.fields.validate(fields_regex='specific_data.data\..*')
    all_fields = devices.fields.get()
    agg_fields = all_fields["agg"]
    root_agg_fields = [x for x in agg_fields if x["is_root"]]
    root_agg_fields = [x["name_qual"] for x in root_agg_fields]
    root_agg_fields = [x for x in root_agg_fields if not x.endswith("_details")]

    pages = []
    cursor = None
    idx = 0
    while True:
        start = datetime.datetime.now()

        page = devices._get_cursor(
            query=query,
            fields=root_agg_fields,
            row_start=idx,
            page_size=1,
            cursor=cursor,
        )
        pages.append(page)
        cursor = page["cursor"]
        end = datetime.datetime.now()
        delta = str(end - start)
        size = len(json.dumps(pages[idx])) / 1024
        page["meta"] = {"delta": delta, "size": size, "idx": idx}
        print(f"asset#: {idx}, delta: {delta}, KB: {size}")
        if not page["assets"] or idx >= 100:
            break
        idx += 1

    time_pages = sorted(pages, key=lambda x: x["meta"]["delta"])
