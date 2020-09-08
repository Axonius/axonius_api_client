#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import os

import axonius_api_client as axonapi  # noqa:F401
from axonius_api_client.connect import Connect
from axonius_api_client.constants import load_dotenv
from axonius_api_client.query_wizard import WizardText
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
        log_level_console="debug",
    )

    # ctx.start()

    devices = ctx.devices
    users = ctx.users
    j = jdump


content = """
type=saved_query, name=boogy, description=vittles, tags="a,b", fields="os.type"
type=complex, field=installed_software, bracket_left=y
type=complex_sub, field=version, operator=earlier_than, value=99
type=complex_sub, field=name, operator=contains, value=chrome
type=simple, field=hostname, value='x'
type=simple, field=hostname, value='x'
type=simple, field=hostname, value='x'
type=simple, field=hostname, value='x', or=y
type=simple, field=hostname, value='x'
"""  # noqa
parser = WizardText(apiobj=devices, log_level="debug")
sqs = parser.parse(content)

for sq in sqs:
    devices.saved_query.add(**sq["sq"])

# try:
#     entries = parser.parse(content)
# except Exception as exc:
#     print(f"----\n{exc}")
#     raise
# else:
#     print(entries)
#     # print(entries[0]["query"])
#     # lines = parser.unparse(entries)
#     # examples = parser.get_examples()
#     # print(examples)

#     # sqs = []
#     # for entry in entries:
#     #     sq = devices.saved_query.add(**entry)
#     #     sqs.append(sq)
