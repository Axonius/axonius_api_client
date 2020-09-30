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
    jreload = axonapi.tools.json_reload
    json_dump = axonapi.tools.json_dump

    def jdump(obj, **kwargs):
        """JSON dump utility."""
        print(jreload(obj, **kwargs))

    ctx = axonapi.Connect(
        url=AX_URL,
        key=AX_KEY,
        secret=AX_SECRET,
        certwarn=False,
        log_level_console="debug",
        log_level_api="debug",
        log_level_http="debug",
    )

    ctx.start()
    devices = ctx.devices
    j = jdump
    fields_map = devices.fields.get()
    agg_fields = fields_map["agg"]
    agg_fields = [x["name"] for x in agg_fields if x["is_root"] and x["selectable"]]
    agg_fields += ["all"]
    ID = "623de6fad018809afa2f07e4305c90c0"
    query = f'(internal_axon_id == "{ID}")'
    asset = devices.get(query=query, fields=agg_fields, include_details=True)[0]


def check_same(idx, field, asset, adapter, data_client_used):
    data = asset["specific_data"][idx]["data"]
    data_value = data.get(field)

    asset_values = asset.get(f"specific_data.data.{field}_details")
    asset_value = asset_values[idx]
    if data_value != asset_value:
        msg = [
            f"field {field} value mismatch",
            f"value in data {data_value}",
            f"value in asset {asset_value}",
            f"adapter {adapter}",
            f"client {data_client_used}",
            f"asset_values {json_dump(asset_values)}",
            f"idx: {idx}",
        ]
        raise Exception("\n".join(msg))
    else:
        msg = [
            f"field {field} value match",
            f"value in data {data_value}",
            f"value in asset {asset_value}",
            f"adapter {adapter}",
            f"client {data_client_used}",
            f"asset_values {json_dump(asset_values)}",
            f"idx: {idx}",
        ]
        print("\n".join(msg))


datas = asset["specific_data"]
adapters = asset["adapters"]
client_used = asset["meta_data.client_used"]
for idx, adapter in enumerate(adapters):
    data = datas[idx]
    data_plugin_name = data["plugin_name"]
    data_client_used = data["client_used"]
    idx_client_used = asset["meta_data.client_used"][idx]

    assert adapter == data_plugin_name, (adapter, data_plugin_name)
    assert data_client_used == idx_client_used, (data_client_used, idx_client_used)
    # check_same(idx, "fetch_time", asset, adapter, data_client_used)
    check_same(idx, "hostname", asset, adapter, data_client_used)
    check_same(idx, "domain", asset, adapter, data_client_used)
