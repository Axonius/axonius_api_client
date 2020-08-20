#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import os

import axonius_api_client as axonapi  # noqa:F401
from axonius_api_client.connect import Connect
from axonius_api_client.constants import load_dotenv
from axonius_api_client.query_wizard import QueryWizardIni
from axonius_api_client.tools import get_path, json_reload


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

    ctx.start()

    devices = ctx.devices
    users = ctx.users
    j = jdump
    ini_dir = get_path(__file__).parent
    ini_file = "wizard_proof.ini"
    ini_path = ini_dir / ini_file
    wizard = QueryWizardIni.from_file(apiobj=devices, path=ini_path)
    final = wizard.parse("combo1")
    print(final["value"]["aql"])
