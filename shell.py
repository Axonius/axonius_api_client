#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import json
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


# fh = open("../../test_export.json")
# tempfh = open("../../test_export_temp.json", mode="w+", encoding="utf-8")
# rows = json.load(fh)
# for row in rows:
#     row = json.dumps(row)
#     tempfh.write(f"{row}\n")

# tempfh.close()

schemas = open("../../schemas.json", encoding="utf-8")
schemas = json.load(schemas)
fields_map = [y for x in schemas for y in x.values()]

fields = [
    "specific_data.data.hostname",
    "specific_data.data.hostname_preferred",
    "adapters_data.active_directory_adapter.hostname",
    "adapters_data.bigfix_adapter.hostname",
    "adapters_data.bitlocker_adapter.hostname",
    "adapters_data.bluecat_adapter.hostname",
    "adapters_data.crowd_strike_adapter.hostname",
    "adapters_data.divvycloud_adapter.hostname",
    "adapters_data.imperva_dam_adapter.hostname",
    "adapters_data.jamf_adapter.hostname",
    "adapters_data.mssql_adapter.hostname",
    "adapters_data.pkware_adapter.hostname",
    "adapters_data.saltstack_enterprise_adapter.hostname",
    "adapters_data.sccm_adapter.hostname",
    "adapters_data.symantec_adapter.hostname",
    "adapters_data.symantec_ccs_adapter.hostname",
    "adapters_data.symantec_dlp_adapter.hostname",
    "adapters_data.tanium_adapter.hostname",
    "adapters_data.tanium_asset_adapter.hostname",
    "adapters_data.tanium_discover_adapter.hostname",
    "adapters_data.tanium_sq_adapter.hostname",
    "adapters_data.tenable_security_center_adapter.hostname",
    "specific_data.data.agent_versions",
    "adapters_data.bigfix_adapter.agent_versions",
    "adapters_data.bitlocker_adapter.agent_versions",
    "adapters_data.crowd_strike_adapter.agent_versions",
    "adapters_data.imperva_dam_adapter.agent_versions",
    "adapters_data.sccm_adapter.agent_versions",
    "adapters_data.symantec_adapter.agent_versions",
    "adapters_data.symantec_ccs_adapter.agent_versions",
    "adapters_data.symantec_dlp_adapter.agent_versions",
    "adapters_data.tanium_adapter.agent_versions",
    "adapters_data.tanium_sq_adapter.agent_versions",
    "specific_data.data.last_seen",
    "adapters_data.active_directory_adapter.last_seen",
    "adapters_data.bigfix_adapter.last_seen",
    "adapters_data.bitlocker_adapter.last_seen",
    "adapters_data.crowd_strike_adapter.last_seen",
    "adapters_data.divvycloud_adapter.last_seen",
    "adapters_data.imperva_dam_adapter.last_seen",
    "adapters_data.jamf_adapter.last_seen",
    "adapters_data.mssql_adapter.last_seen",
    "adapters_data.pkware_adapter.last_seen",
    "adapters_data.sccm_adapter.last_seen",
    "adapters_data.symantec_adapter.last_seen",
    "adapters_data.symantec_ccs_adapter.last_seen",
    "adapters_data.symantec_dlp_adapter.last_seen",
    "adapters_data.tanium_adapter.last_seen",
    "adapters_data.tanium_asset_adapter.last_seen",
    "adapters_data.tanium_discover_adapter.last_seen",
    "adapters_data.tanium_sq_adapter.last_seen",
    "adapters_data.tenable_security_center_adapter.last_seen",
]

# schemas = devices.fields.get()
getargs = {
    "help_detailed": None,
    "field_null": True,
    "field_join_value": "!",
    "field_join_trim": 0,
    "export_overwrite": True,
    "export_file": "new_test.csv",
    "export_path": "/Users/jimbo",
    "do_echo": True,
    "table_format": "fancy_grid",
    "table_max_rows": 5,
    "export_schema": False,
    "field_titles": False,
    "field_join": False,
    "field_explode": "",
    "field_flatten": False,
    "field_excludes": (),
    "field_null_value": None,
    "report_adapters_missing": False,
    "tags_add": (),
    "tags_remove": (),
}
cb_cls = axonapi.api.asset_callbacks.get_callbacks_cls("csv")
cb = cb_cls(
    apiobj=devices,
    fields=fields,
    query=None,
    state={},
    fields_map=schemas,
    getargs=getargs,
)
cb.start()

idx = 0
idx_dt = axonapi.tools.dt_now()
start_dt = axonapi.tools.dt_now()

fh = open("../../test_export_temp.json", encoding="utf-8")
for line in fh.readlines():
    row = json.loads(line.strip())
    cb.row(row=row)
    idx += 1
    if idx % 1000 == 0:
        secs = axonapi.tools.dt_sec_ago(idx_dt)
        # print(f"1000 in {secs}")
        idx_dt = axonapi.tools.dt_now()

took = axonapi.tools.dt_sec_ago(start_dt)
print(f"took {took}")
