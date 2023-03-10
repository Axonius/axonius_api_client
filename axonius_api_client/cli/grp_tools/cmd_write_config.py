# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import CONTEXT_SETTINGS
from ..options import AUTH, add_options
from .grp_common import export_env
from .grp_options import OPT_ENV

OPTIONS = [*AUTH, OPT_ENV]


@click.command(name="write-config", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, env):
    """Create/Update a '.env' file with url, key, and secret."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    data = {"api_secret": secret, "api_key": key}
    export_env(data=data, env=env, url=client.AUTH.http.url)
    ctx.exit(0)
