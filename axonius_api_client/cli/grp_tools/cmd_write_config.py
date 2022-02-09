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
    path_str = f"{path}"

    if not path.is_file():
        click.secho(message=f"Creating file {path_str!r}", err=True, fg="green")
        path.touch()
        path.chmod(0o600)
    else:
        click.secho(message=f"Updating file {path_str!r}", err=True, fg="green")

    click.secho(
        message=f"Setting AX_URL, AX_KEY, and AX_SECRET in {path_str!r}", err=True, fg="green"
    )
    dotenv.set_key(dotenv_path=path_str, key_to_set="AX_URL", value_to_set=url)
    dotenv.set_key(dotenv_path=path_str, key_to_set="AX_KEY", value_to_set=key)
    dotenv.set_key(dotenv_path=path_str, key_to_set="AX_SECRET", value_to_set=secret)
