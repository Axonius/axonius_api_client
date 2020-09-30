#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script example to parse WMI Scan data.

Will parse WMI scan data to find all users who have logged into a system in the past
N days.
"""
import datetime
import os

import dateutil

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

    def parse_dt(value):
        """Pass."""
        return dateutil.parser.parse(value["last_use_date"])

    def check_last_login(wmi_user: dict, days: int = 14):
        """Pass."""
        check_date = axonapi.tools.dt_now() - datetime.timedelta(days=days)
        value = wmi_user.get("last_use_date")
        return bool(value and dateutil.parser.parse(value) >= check_date)

    def parse_asset_wmi_user(asset, days=14):
        """Pass."""
        key = "adapters_data.wmi_adapter.users"
        wmi_users = asset.get(key, [])
        new_wmi_users = sorted(
            [x for x in wmi_users if check_last_login(wmi_user=x, days=days)],
            key=parse_dt,
        )
        asset[key] = new_wmi_users

    def do_row(self, row):
        """Pass."""
        self.process_tags_to_add(row=row)
        self.process_tags_to_remove(row=row)
        self.add_report_adapters_missing(row=row)
        days = self.GETARGS.get("last_days_cb", 14)
        parse_asset_wmi_user(asset=row, days=days)

        for schema in self.schemas_selected:
            self.do_excludes(row=row, schema=schema)
            self.do_add_null_values(row=row, schema=schema)
            self.do_flatten_fields(row=row, schema=schema)

        new_rows = self.do_explode_field(row=row)
        for new_row in new_rows:
            self.do_join_values(row=new_row)
            self.do_change_field_titles(row=new_row)

        return new_rows

    axonapi.api.asset_callbacks.base.Base.do_row = do_row

    assets = devices.get_by_saved_query(
        name="WADTS 14 days",
        export="csv",
        export_file="blah.csv",
        last_days_cb=14,
        export_overwrite=True,
    )
