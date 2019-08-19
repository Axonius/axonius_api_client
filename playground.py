#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json


def jdump(obj):
    """JSON dump utility."""
    print(json.dumps(obj, indent=2))


if __name__ == "__main__":
    import axonius_api_client as axonapi

    try:
        ctx = axonapi.cli.main(standalone_mode=False)
        try:
            devices = ctx.obj.devices
            adapters = ctx.obj.adapters
            users = ctx.obj.users
        except Exception:
            pass
    except SystemExit:
        # print("system exit")
        pass
