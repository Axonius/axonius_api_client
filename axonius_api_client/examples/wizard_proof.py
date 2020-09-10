#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import os

import axonius_api_client as axonapi  # noqa:F401
import click
from axonius_api_client import Connect, WizardCsv, WizardText
from axonius_api_client.constants import load_dotenv
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
        log_request_attrs="url",
    )

    devices = ctx.devices
    users = ctx.users
    j = jdump


"type, value, description, tags, flags, fields"

content_txt = """
simple      "hostname contains test.domain"
complex     "or not ( installed_software"
complex_sub "version earlier_than 99"
simple      "or not ) hostname contains test.domain"
"""  # noqa

"""
[
    {'type': 'saved_query', 'name': '', 'description': ''},
    {'type': 'simple', 'value': ''},
    {'type': 'saved_query', 'name': '', 'description': ''},
]
# axonshell devices saved-query wiz-add-from-csv --file pg.csv
# axonshell devices saved-query wiz-add --name '' --description '' --wiz simple "hostname contains test.domain"
# axonshell devices get --wiz simple "hostname contains test.domain" --wiz complex "installed_software"

"""  # noqa
content_csv = """
type, query, name, description, tags, fields
saved_query, "", "bbb", "ccc", "a,b", "hostname,os.type,default"
simple,"or not ( ) hostname contains test.domain"
"""  # noqa
text_parser = WizardText(apiobj=devices, log_level="debug")
sqs = text_parser.parse(content_txt)
# print(text_parser.get_examples())

csv_parser = WizardCsv(apiobj=devices, log_level="debug")
# sqs = csv_parser.parse_path("~/pg.csv")
# sqs = csv_parser.parse(content_csv)

# for sq in sqs:
#     devices.saved_query.add(**sq)


def callback(ctx, param, value):
    print(param, value)


@click.command()
@click.option("--wiz", nargs=2, callback=callback, multiple=True)
def cli(wiz):
    print(wiz)


# cli()
