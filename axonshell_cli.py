#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
from __future__ import absolute_import, division, print_function, unicode_literals

if __name__ == "__main__":
    import axonius_api_client as axonapi

    try:
        # ctx = axonapi.cli.main(standalone_mode=False)
        ctx = axonapi.cli.main()
    except SystemExit:
        pass
