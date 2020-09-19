#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import os

import axonius_api_client as axonapi  # noqa: F401
from axonius_api_client.connect import Connect
from axonius_api_client.constants import load_dotenv
from axonius_api_client.tools import json_reload


def jdump(obj, **kwargs):
    """JSON dump utility."""
    print(json_reload(obj, **kwargs))


if __name__ == "__main__":
    load_dotenv()

    AX_URL = os.environ["AX_URL"]
    AX_KEY = os.environ["AX_KEY"]
    AX_SECRET = os.environ["AX_SECRET"]

    ctx = Connect(
        url=AX_URL,
        key=AX_KEY,
        secret=AX_SECRET,
        certwarn=False,
        # log_console=True,
    )

    ctx.start()
    devices = ctx.devices
    users = ctx.users
    adapters = ctx.adapters
    enforcements = ctx.enforcements
    system = ctx.system
    j = jdump
    tmpl = 'specific_data.data.hostname == regex("{value}", "i") or specific_data.data.name == regex("{value}", "i") or specific_data.data.id == regex("{value}", "i")'  # noqa

    user_assets = users.get(fields=["associated_devices"])
    for user_asset in user_assets:
        assdvcs = list(user_asset.get("specific_data.data.associated_devices", []) or [])
        username = user_asset.get("specific_data.data.username")
        if not assdvcs:
            print(f"NO associated_devices for user {username}")
            continue

        for assdvc in assdvcs:
            caption = assdvc.get("device_caption")
            query = tmpl.format(value=caption)
            found_assdvc = devices.get(query=query)
            if not found_assdvc:
                print(
                    f"Unable to find associated_devices for user {username} using query {query}"
                )
                continue
            print(found_assdvc)
