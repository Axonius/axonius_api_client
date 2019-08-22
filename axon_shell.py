#!/usr/bin/env python -i
# -*- coding: utf-8 -*-
"""Example of basic object setup for API."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json

import dotenv

import axonius_api_client

dotenv.load_dotenv()


AX_URL = os.environ.get("AX_URL", None) or None
AX_KEY = os.environ.get("AX_KEY", None) or None
AX_SECRET = os.environ.get("AX_SECRET", None) or None


def jdump(obj, **kwargs):
    """Pass."""
    kwargs.setdefault("indent", 2)
    kwargs.setdefault("sort_keys", True)
    print(json.dumps(obj, **kwargs))


class Connect(object):
    """Pass."""

    def __init__(self, url, key, secret):
        """Pass."""
        self.http = axonius_api_client.http.HttpClient(url=url)
        self.auth = axonius_api_client.auth.AuthKey(
            http_client=self.http, key=key, secret=secret
        )
        self.auth.login()
        self.users = axonius_api_client.api.Users(auth=self.auth)
        self.devices = axonius_api_client.api.Devices(auth=self.auth)
        self.enforcements = axonius_api_client.api.Enforcements(auth=self.auth)
        self.adapters = axonius_api_client.api.Adapters(auth=self.auth)
        self.actions = axonius_api_client.api.Actions(auth=self.auth)


if __name__ == "__main__":
    ctx = Connect(url=AX_URL, key=AX_KEY, secret=AX_SECRET)
