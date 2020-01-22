#!/usr/bin/env python -i
# -*- coding: utf-8 -*-
"""Utilities for this package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import re

import axonius_api_client as axonapi

from axonius_api_client import tools

# from axonius_api_client.cli.serial import join_cr, is_los, is_list, is_dos


def key_field_match(key, fields):
    """Pass."""
    return any([re.search(field, key, re.I) for field in fields])


def filter_row_field(obj, fields):
    """Pass."""
    return {k: v for k, v in obj.items() if not key_field_match(key=k, fields=fields)}


def filter_rows_fields(raw_data, fields=None):
    """Pass."""
    raw_data = tools.listify(obj=raw_data, dictkeys=False)
    fields = tools.listify(obj=fields)
    return [filter_row_field(obj=r, fields=fields) for r in raw_data]


if __name__ == "__main__":
    import os

    axonapi.cli.cli_constants.load_dotenv()

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
        log_console=True,
    )

    ctx.start()

    devices = ctx.devices
    users = ctx.users
    adapters = ctx.adapters

    obj_to_table = axonapi.cli.serial.obj_to_table
    rows = devices.get(max_rows=1,)
    filtered_rows = filter_rows_fields(
        raw_data=rows, fields=["^adapters$", "internal_axon_id", "adapter_list_length"]
    )
    rows_table = obj_to_table(
        ctx=None, raw_data=rows, joiner="\n", table_format="simple"
    )
    filtered_rows_table = obj_to_table(
        ctx=None, raw_data=filtered_rows, joiner="\n", table_format="simple"
    )
