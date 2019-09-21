# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import os

import click
import dotenv
import requests

from .. import tools


def load_dotenv():
    """Pass."""
    AX_ENV = os.environ.get("AX_ENV", "")

    if AX_ENV:
        path = tools.path(obj=AX_ENV)
    else:
        path = tools.path(obj=os.getcwd()) / ".env"

    dotenv.load_dotenv(format(path))


load_dotenv()

HISTPATH = os.path.expanduser("~")

HISTFILE = ".python_history"

CONTEXT_SETTINGS = {"auto_envvar_prefix": "AX"}

REASON = "Export format {ef!r} is unsupported!  Must be one of: {sf}"

QUOTING = csv.QUOTE_NONNUMERIC

SCRIPT = "axonshell"

KV_TMPL = "{k}: {v}"

MAX_LEN = 30000

MAX_STR = "...TRIMMED - {c} items over max cell length {mc}"

SHELL_BANNER = """Welcome human. We have some refreshments available for you:

    - ctx: Click context object
    - client/c: Instance of axonius_api_client.connect.Connect
    - devices/d: Instance of axonius_api_client.api.Devices
    - users/u: Instance of axonius_api_client.api.Users
    - adapters/a: Instance of axonius_api_client.api.Adapters
    - jdump/j: Helper function to pretty print python objects
"""

SHELL_EXIT = """Goodbye human. We hope you enjoyed your stay."""

HIDDEN = ["secret", "key", "password"]

OK_ARGS = {"fg": "green", "bold": True, "err": True}

OK_TMPL = "** {msg}"

WARN_ARGS = {"fg": "yellow", "bold": True, "err": True}

WARN_TMPL = "** WARNING: {msg}"

ERROR_ARGS = {"fg": "red", "bold": True, "err": True}

ERROR_TMPL = "** ERROR: {msg}"

SSLWARN_MSG = (
    "Unverified HTTPS request! Set AX_CERT environment variable or "
    "--cert option to the path of a CA bundle!"
)

SSLWARN_CLS = requests.urllib3.exceptions.InsecureRequestWarning


SETTING_TYPE_MAP = {
    "bool": click.BOOL,
    "integer": click.INT,
    "number": click.INT,
    "file": click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        allow_dash=False,
        path_type=None,
    ),
}
