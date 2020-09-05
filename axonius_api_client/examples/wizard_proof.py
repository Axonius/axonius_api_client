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
        # log_level_console="info",
    )

    # ctx.start()

    devices = ctx.devices
    users = ctx.users
    j = jdump

content = """
field=last_seen, operator=last_hours, value=24
type=complex, field=agg:installed_software
type=complex_sub, field=name, value="Google Chrome"
type=complex_sub, field=version, operator=earlier_than, value=99
"""

content = """
type=saved_query, sq_name=boogy, sq_description=vittles, sq_tags="a,b", sq_fields="hostname, aws:boo"
type=simple, or=y, not=y, field=last_seen, operator=last_hours, value=24
type=simple, or=y, not=n, field=last_seen, operator=last_hours, value=24
type=simple, or=n, not=n, field=last_seen, operator=last_hours, value=24
type=simple, or=n, not=y, field=last_seen, operator=last_hours, value=24
type=complex_sub, field=name, operator=equals, value="Google Chrome"
type=complex_sub, field=version, operator=earlier_than, value=99
type=complex, or=y, not=y, left_bracket=y, right_bracket=y, field=agg:installed_software
"""  # noqa

content = """
type=saved_query, name=boogy, description=vittles, tags="a,b", fields="os.type"
type=simple, field=last_seen, operator=last_hours, value=24
type=simple, field=last_seen, operator=last_hours, value=24, bracket=left
type=simple, field=last_seen, operator=last_hours, value=24, logic=or not

"""  # noqa
content = """
type=complex, field=installed_software, logic=and
type=complex_sub, field=version, operator=earlier_than, value=99
"""  # noqa
parser = WizardText(apiobj=devices, log_level="debug")
try:
    entries = parser.parse(content)
except Exception as exc:
    print(f"----\n{exc}")
    raise
else:
    print(entries[0]["query"])
    lines = parser.unparse(entries)
    examples = parser.get_examples()
    # print(examples)

    sqs = []
    for entry in entries:
        sq = devices.saved_query.add(**entry)
        sqs.append(sq)
