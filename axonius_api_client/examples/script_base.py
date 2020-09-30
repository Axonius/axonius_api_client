#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base example for setting up the API client."""
import os

import axonius_api_client as axonapi  # noqa: F401
from axonius_api_client.connect import Connect
from axonius_api_client.constants import load_dotenv
from axonius_api_client.tools import json_reload


def j(obj, **kwargs):
    """JSON dump utility."""
    print(json_reload(obj, **kwargs))


if __name__ == "__main__":
    # read the API key, API secret, and URL from a ".env" file
    load_dotenv()

    AX_URL = os.environ["AX_URL"]
    AX_KEY = os.environ["AX_KEY"]
    AX_SECRET = os.environ["AX_SECRET"]

    # create a client using the url, key, and secret
    client = Connect(url=AX_URL, key=AX_KEY, secret=AX_SECRET)

    # start the client, will perform login to URL using key & secret
    client.start()

    # work with device assets
    devices = client.devices

    # work with user assets
    users = client.users

    # work with adapters and adapter connections
    adapters = client.adapters

    # work with enforcements
    enforcements = client.enforcements

    # work with users, roles, global settings, and more
    system = client.system

    # work with instances
    instances = client.instances

    # work with dashboards and discovery cycles
    dashboard = client.dashboard
