# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import click
import dotenv

from ... import tools


@click.command(name="write-config")
@click.option(
    "--url",
    "-u",
    "url",
    required=True,
    help="URL of Axonius instance.",
    metavar="URL",
    prompt="URL of Axonius instance",
)
@click.option(
    "--key",
    "-k",
    "key",
    required=True,
    help="API Key of user in Axonius instance.",
    metavar="KEY",
    prompt="API Key of user in Axonius instance",
    hide_input=True,
)
@click.option(
    "--secret",
    "-s",
    "secret",
    required=True,
    help="API Secret of user in Axonius instance.",
    metavar="SECRET",
    prompt="API Secret of user in Axonius instance",
    hide_input=True,
)
@click.pass_context
def cmd(ctx, url, key, secret):
    """Create/Update a '.env' file with url, key, and secret.

    File is created in the current working directory.
    """
    ctx.obj.start_client(url=url, key=key, secret=secret)

    cwd = os.getcwd()
    path = tools.path(cwd) / ".env"

    if not path.is_file():
        msg = "Creating file {!r}".format(format(path))
        click.secho(message=msg, err=True, fg="green")

        path.touch()
        path.chmod(0o600)

    msg = "Setting AX_URL, AX_KEY, and AX_SECRET in {!r}".format(format(path))
    click.secho(message=msg, err=True, fg="green")
    dotenv.set_key(dotenv_path=path, key_to_set="AX_URL", value_to_set=url)
    dotenv.set_key(dotenv_path=path, key_to_set="AX_KEY", value_to_set=key)
    dotenv.set_key(dotenv_path=path, key_to_set="AX_SECRET", value_to_set=secret)
