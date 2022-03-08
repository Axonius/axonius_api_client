# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...constants.api import USE_CA_PATH
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTIONS = [
    *AUTH,
    click.option(
        "--enable/--disable",
        "-e/-d",
        "value",
        help=(f"Enable or disable {USE_CA_PATH!r}"),
        is_flag=True,
        required=True,
        show_default=True,
        show_envvar=True,
    ),
]


@click.command(name="ca-enable", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, value):
    """Enable/disable 'Use custom CA certificate' setting."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.settings_global

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.ca_enable(value=value)
        ctx.obj.echo_ok(f"Updated {USE_CA_PATH!r} to {value}")
        click.secho("\n".join(apiobj.cas_to_str(config=data)))
    ctx.exit(0)
