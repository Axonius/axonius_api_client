#!/usr/bin/env python -i
# -*- coding: utf-8 -*-
"""Example of getting devices by a saved query."""

if __name__ == "__main__":
    import json
    import os

    import axonius_api_client as axonapi

    tools = axonapi.tools
    axonapi.cli.cli_constants.load_dotenv()

    AX_URL = os.environ["AX_URL"]
    AX_KEY = os.environ["AX_KEY"]
    AX_SECRET = os.environ["AX_SECRET"]
    SQ_NAME = os.environ.get("AX_SQ_NAME", "Managed Devices")
    FORMAT = os.environ.get("AX_FORMAT", "json")

    def jdump(obj, **kwargs):
        """JSON dump utility."""
        print(axonapi.tools.json_reload(obj, **kwargs))

    ctx = axonapi.Connect(
        url=AX_URL,
        key=AX_KEY,
        secret=AX_SECRET,
        certwarn=False,
        log_level_console="debug",
        log_level_api="debug",
        log_console=True,
    )

    ctx.start()

    devices = ctx.devices
    users = ctx.users
    adapters = ctx.adapters

    results = devices.get_by_saved_query(name=SQ_NAME)

    if FORMAT.lower() == "json":
        export_results = json.dumps(results, indent=4)
    elif FORMAT.lower() == "csv":
        joiner = "\n"  # join multiple items in inner cell with this character
        export_results = axonapi.cli.serial.obj_to_csv(
            ctx=None,
            raw_data=results,
            joiner=joiner,
        )

    else:
        msg = "Invalid format {}, must be one of 'json' or 'csv'".format(FORMAT)
        raise Exception(msg)
