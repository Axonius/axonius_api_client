#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import os

import axonius_api_client as axonapi  # noqa:F401
from axonius_api_client.connect import Connect
from axonius_api_client.constants import load_dotenv
from axonius_api_client.query_wizard import Wizard  # , WizardText
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
        log_console=True,
        # log_level_console="info",
    )

    # ctx.start()

    devices = ctx.devices
    users = ctx.users
    j = jdump


content = """
type=simple, field=last_seen, operator=last_hours, or=y, not=y, value=24
type=simple, field=last_seen, operator=last_hours, or=y, not=n, value=24
type=simple, field=last_seen, operator=last_hours, not=n, value=24
type=simple, field=last_seen, operator=last_hours, or=y, not=y, value=24
type=complex, or=y, not=y, field=agg:installed_software, left_bracket=y
type=complex_sub, field=name, operator=equals, value="Google Chrome"
type=complex_sub, field=version, operator=earlier_than, value=99
"""
wizard = Wizard(apiobj=devices, log_level="debug")
aql, exprs = wizard.parse_text_str(content=content)
a = devices.saved_query.add(
    name="boom",
    query=aql,
    expressions=exprs,
    description="foo bar",
    tags=["a", "bc", "def"],
)
