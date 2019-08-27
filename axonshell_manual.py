#!/usr/bin/env python -i
# -*- coding: utf-8 -*-
"""Utilities for this package."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

import dotenv

import axonius_api_client as axonapi

dotenv.load_dotenv()

AX_URL = os.environ["AX_URL"]
AX_KEY = os.environ["AX_KEY"]
AX_SECRET = os.environ["AX_SECRET"]


def jdump(obj, **kwargs):
    """JSON dump utility."""
    print(axonapi.tools.json.re_load(obj, **kwargs))


if __name__ == "__main__":
    ctx = axonapi.tools.Connect(
        url=AX_URL, key=AX_KEY, secret=AX_SECRET, certwarn=False
    )
    try:
        ctx.start()
    except Exception as exc:
        print(exc)
