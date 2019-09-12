#!/usr/bin/env python -i
# -*- coding: utf-8 -*-
"""Utilities for this package."""
from __future__ import absolute_import, division, print_function, unicode_literals


if __name__ == "__main__":
    import os

    import axonius_api_client as axonapi

    tools = axonapi.tools
    axonapi.cli.context.load_dotenv()

    AX_URL = os.environ["AX_URL"]
    AX_KEY = os.environ["AX_KEY"]
    AX_SECRET = os.environ["AX_SECRET"]

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

    with axonapi.cli.context.exc_wrap(wraperror=True):
        ctx.start()
