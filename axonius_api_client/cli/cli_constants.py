# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import os

import click
import dotenv
import requests

from .. import tools

AX_ENV = os.environ.get("AX_ENV", "").strip() or os.getcwd()


def load_dotenv(ax_env=AX_ENV, reenv=False, verbose=False):
    """Pass."""
    if reenv:
        ax_env = os.environ.get("AX_ENV", "").strip() or os.getcwd()

    ax_env_path = tools.path(obj=ax_env)

    if ax_env_path.is_dir():
        ax_env_path = ax_env_path / ".env"

    return (
        dotenv.load_dotenv(dotenv_path=format(ax_env_path), verbose=verbose),
        ax_env_path,
    )


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

SSLWARN_MSG = """Unverified HTTPS request!

To enable certificate validation:
  * Set the variable: AX_CERTPATH=/path/to/cert_or_ca_bundle
  * Supply the option: -cp/--cert-path /path/to/cert_or_ca_bundle

To silence this message:
  * Set the variable: AX_CERTWARN=n
  * Supply the option: -ncw/--no-cert-warn
"""

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
