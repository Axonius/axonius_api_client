#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import json
import os

import axonius_api_client as axonapi  # noqa:F401
from axonius_api_client import Connect, wizard
from axonius_api_client.constants import load_dotenv
from axonius_api_client.tools import json_reload
from axonius_api_client.wizard.constants import Docs


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
        log_file=True,
        log_level_console="debug",
        log_request_attrs="url",
    )

    devices = ctx.devices
    users = ctx.users
    j = jdump


content_text = Docs.EX_TEXT
content_json = Docs.EX_DICT
content_dict = json.loads(content_json)
content_csv = Docs.EX_CSV

cli = f"""
axonshell devices saved-query wiz-add-from-csv --file blah.csv

axonshell devices saved-query wiz-add
    --name 'test'
    --description 'test'
    --wiz simple "{Docs.EX_SIMPLE1}"
    --wiz simple "{Docs.EX_SIMPLE2}"
    --wiz simple "{Docs.EX_SIMPLE3}"
    --wiz simple "{Docs.EX_SIMPLE4}"
    --wiz complex "{Docs.EX_COMPLEX1}"
    --wiz text_file "blah.txt"
    --wiz json_file "blah.json"

axonshell devices get
    --wiz simple "{Docs.EX_SIMPLE1}"
    --wiz simple "{Docs.EX_SIMPLE2}"
    --wiz simple "{Docs.EX_SIMPLE3}"
    --wiz simple "{Docs.EX_SIMPLE4}"
    --wiz complex "{Docs.EX_COMPLEX1}"
    --wiz text_file "blah.txt"
    --wiz json_file "blah.json"

"""
# content_csv = """z"""
parser = wizard.Wizard(apiobj=devices, log_level="debug")
parser_csv = wizard.WizardCsv(apiobj=devices, log_level="debug")
parser_text = wizard.WizardText(apiobj=devices, log_level="debug")

# result = parser.parse(entries=content_dict)
# sq = devices.saved_query.add(name="sq from list of dict", **result)

# result_text = parser_text.parse(content=content_text)
# sq = devices.saved_query.add(name="sq from text", **result_text)

# result_csv = parser_csv.parse(content=content_csv)
# sqs = [devices.saved_query.add(**sq) for sq in result_csv]


# sq to wiz?
