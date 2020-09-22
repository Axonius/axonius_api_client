# -*- coding: utf-8 -*-
"""Utilities for this package."""
import json
import os
from datetime import datetime, timedelta

import axonius_api_client as axonapi
from axonius_api_client.constants import ALL_NAME

PAGE_SIZE = 10
MAX_PAGE_TOOK_SECS = 10
MAX_ROW_KB = 1000
MAX_KEY_KB = 2000
ROW_TMPL = (
    "#{row_num} {axid} KB: {row_kb:0.2f}, KB TOTAL: "
    "{rows_size:0.2f}, page took: {page_took:0.2f}"
)
KEY_TMPL = "               KEY over {MAX_KEY_KB}: {k}, KB: {vkb:0.2f}"


def _field_wanted(field):
    name = field.get("name_qual")
    is_root = field.get("is_root")
    is_selectable = field.get("selectable")
    is_all = field["name_base"] == ALL_NAME
    is_complex = field.get("is_complex")
    return name and is_root and is_selectable and not is_all and not is_complex


def calc_row_size(self, row):
    if not hasattr(self, "_rows_size"):
        self._rows_size = 0

    row_size = len(json.dumps(row))
    row_kb = row_size / 1024
    self._rows_size += row_kb

    axid = row["internal_axon_id"]
    row_num = self.STATE.get("rows_processed_total", 0)
    fetch_secs = self.STATE.get("fetch_seconds_this_page", 0)

    if not fetch_secs >= float(MAX_PAGE_TOOK_SECS):
        return

    msg = ROW_TMPL.format(
        row_num=row_num,
        axid=axid,
        row_kb=row_kb,
        rows_size=self._rows_size,
        page_took=fetch_secs,
    )
    self.echo(msg=msg, warning=True, abort=False)

    if row_kb >= float(MAX_ROW_KB):
        for k, v in row.items():
            vsize = len(json.dumps(v))
            vkb = vsize / 1024
            if vkb >= float(MAX_KEY_KB):
                msg = KEY_TMPL.format(MAX_KEY_KB=MAX_KEY_KB, k=k, vkb=vkb)
                self.echo(msg=msg, error=True, abort=False)


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
        # log_file=True,
        # log_level_package="info",
        # log_level_console="info",
        # log_level_api="info",
        # log_level_http="info",
        # log_console=True,
    )

    ctx.start()
    devices = ctx.devices

    now = datetime.utcnow()
    this_time = now.isoformat(sep=" ", timespec="seconds")
    last_time = (now - timedelta(days=1)).isoformat(sep=" ", timespec="seconds")
    filters = [
        f'(specific_data.data.fetch_time < date("{this_time}"))',
        f'(specific_data.data.fetch_time >= date("{last_time}"))',
    ]
    query = " and ".join(filters)

    agg_fields = devices.fields.get().get("agg")
    get_fields = [field.get("name_qual") for field in agg_fields if _field_wanted(field)]
    get_fields.extend(
        ["specific_data", "specific_data.data.network_interfaces.ips", "agent_versions"]
    )

    start_all = datetime.now()
    # count = devices.count(query=query)
    # print(f"About to fetch {count} assets with page size {PAGE_SIZE}")
    # time.sleep(3)

    assets = devices.get(
        query=query,
        fields=get_fields,
        fields_default=False,
        max_rows=1,
        # page_size=PAGE_SIZE,
        # custom_cbs=[calc_row_size],
        # page_progress=None,
        do_echo=True,
        include_details=True,
        # might be better than specific_data!?
    )
