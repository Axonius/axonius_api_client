#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Output all of the fields for all of the adapters in Axonius."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import os
import sys

import axonius_api_client

if "AX_URL" not in os.environ:
    print("You must set the AX_URL environment variable!")
    sys.exit(1)

if "AX_KEY" not in os.environ:
    print("You must set the AX_KEY environment variable!")
    sys.exit(1)

if "AX_SECRET" not in os.environ:
    print("You must set the AX_SECRET environment variable!")
    sys.exit(1)

AX_URL = os.environ["AX_URL"]
AX_KEY = os.environ["AX_KEY"]
AX_SECRET = os.environ["AX_SECRET"]


def jdump(obj):
    """JSON dump utility."""
    print(json.dumps(obj, indent=2))


def gen_fields(fields):
    """Generate a dict of all of the generic and adapter specific fields."""
    ret = {
        adapter: [field["name"] for field in fields]
        for adapter, fields in fields["specific"].items()
    }
    ret.update({"generic": [field["name"] for field in fields["generic"]]})
    return ret


logclient = False
loglevel = "warning"
logfile = None

level_client = logging.DEBUG if logclient else logging.WARNING

if loglevel == "debug":
    logfmt = "%(levelname)-8s [%(name)s:%(funcName)s()] %(message)s"
else:
    logfmt = "%(levelname)-8s %(message)s"

level = getattr(logging, loglevel.upper())
logging.basicConfig(format=logfmt, level=level, filename=logfile)

http = axonius_api_client.http.HttpClient(url=AX_URL)
http._log.setLevel(level_client)

auth = axonius_api_client.auth.AuthKey(http_client=http, key=AX_KEY, secret=AX_SECRET)

auth.login()

users = axonius_api_client.api.Users(auth=auth)
devices = axonius_api_client.api.Devices(auth=auth)
# enforcements = axonius_api_client.api.Enforcements(auth=auth)
# adapters = axonius_api_client.api.Adapters(auth=auth)
# actions = axonius_api_client.api.Actions(auth=auth)

all_fields = {
    "users": gen_fields(fields=users.get_fields()),
    "devices": gen_fields(fields=devices.get_fields()),
}

jdump(all_fields)
