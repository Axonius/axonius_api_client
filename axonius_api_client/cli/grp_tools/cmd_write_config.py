# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import os

import click
import dotenv

from ...tools import get_path
from ..options import AUTH, add_options


@click.command(name="write-config")
@add_options(AUTH)
@click.pass_context
def cmd(ctx, url, key, secret):
    """Create/Update a '.env' file with url, key, and secret.

    File is created in the current working directory.
    """
    ctx.obj.start_client(url=url, key=key, secret=secret)

    cwd = os.getcwd()
    path = get_path(cwd) / ".env"

    if not path.is_file():
        msg = "Creating file {!r}".format(format(path))
        click.secho(message=msg, err=True, fg="green")

        path.touch()
        path.chmod(0o600)

    path = format(path)
    msg = "Setting AX_URL, AX_KEY, and AX_SECRET in {!r}".format(format(path))
    click.secho(message=msg, err=True, fg="green")
    dotenv.set_key(dotenv_path=path, key_to_set="AX_URL", value_to_set=url)
    dotenv.set_key(dotenv_path=path, key_to_set="AX_KEY", value_to_set=key)
    dotenv.set_key(dotenv_path=path, key_to_set="AX_SECRET", value_to_set=secret)
