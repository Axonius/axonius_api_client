# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from axonius_api_client.cli.context import CONTEXT_SETTINGS, click
from axonius_api_client.cli.options import AUTH, add_options

OPTIONS = [
    *AUTH
]


@click.command(name="get-spec", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get the OpenAPI YAML specification file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        yaml = client.openapi.get_spec()

    click.secho(yaml)
    ctx.exit(0)
