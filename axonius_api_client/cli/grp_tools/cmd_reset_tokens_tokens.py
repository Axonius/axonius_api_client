# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, WRITE_ENV, add_options
from .grp_common import handle_keys

OPTIONS = [*AUTH, *WRITE_ENV]


@click.command(name="reset-tokens-tokens", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, env_file, write_env, config, export_format):
    """Reset API tokens using API key and secret."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.instances.reset_api_keys()

    handle_keys(
        ctx=ctx,
        url=url,
        data=data,
        write_env=write_env,
        env_file=env_file,
        config=config,
        export_format=export_format,
    )
    ctx.exit(0)
