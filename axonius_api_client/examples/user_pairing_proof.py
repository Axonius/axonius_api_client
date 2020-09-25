#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import os

import axonius_api_client as axonapi  # noqa: F401
from axonius_api_client.connect import Connect
from axonius_api_client.constants import load_dotenv
from axonius_api_client.tools import json_reload, listify

FIND_DVC_QUERY_TMPL = (
    '(specific_data.data.hostname == "{value}") or ' '(specific_data.data.name == "{value}")'
)
ASS_DVC_FIELD = "specific_data.data.associated_devices"
AGENT_VERSIONS_FIELD = "specific_data.data.agent_versions"
DVC_FIELDS = [AGENT_VERSIONS_FIELD]
AGENT_CHECKS = [
    {
        "name": "CrowdStrike Agent",
        "status": "normal",
        "version": "5.36.11809.0",
    }
]


def jdump(obj, **kwargs):
    """JSON dump utility."""
    print(json_reload(obj, **kwargs))


def parse_user(user, client):
    ass_dvcs = listify(user.get(ASS_DVC_FIELD, []))
    # username = listify(asset.get("specific_data.data.username"), [])

    if not ass_dvcs:
        # print(f"NO associated devices found for user {username}")
        return

    for ass_dvc in ass_dvcs:
        dvc = parse_ass_dvc(user=user, ass_dvc=ass_dvc, client=client)
        check_agents(user=user, dvc=dvc)


def check_agents(user, dvc):
    agents = listify(dvc.get(AGENT_VERSIONS_FIELD, []))
    for agent in agents:
        for check in AGENT_CHECKS:
            pass


def parse_ass_dvc(user, ass_dvc, client):
    username = listify(user.get("specific_data.data.username"), [])
    caption = ass_dvc.get("device_caption")
    query = FIND_DVC_QUERY_TMPL.format(value=caption)
    found = client.devices.get(query=query, fields=DVC_FIELDS)
    # NEED TO PASS devices apiobj

    if not found:
        print(f"No devices found that match associated device {caption} for " f"user {username}")
        return

    if len(found) > 1:
        print(
            f"Too many devices ({len(found)}) found that match associated device "
            f"{caption} for user {username}"
        )
        return

    return found[0]


j = jdump


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
    )

    ctx.start()
    devices = ctx.devices
    users = ctx.users

    assets = users.get(fields=[ASS_DVC_FIELD])

    for user in assets:
        parse_user(user=user, client=ctx)
