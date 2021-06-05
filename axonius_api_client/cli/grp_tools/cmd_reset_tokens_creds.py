# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import CREDS, URL, WRITE_ENV, add_options
from .grp_common import handle_keys

OPTIONS = [URL, *CREDS, *WRITE_ENV]


@click.command(name="reset-tokens-creds", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, user_name, password, env_file, write_env, config, export_format):
    """Reset API tokens using username and password."""
    client = ctx.obj.get_client(url=url)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.signup.reset_api_keys(user_name=user_name, password=password)

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
