# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_EXPORT_FORMAT, OPT_SET_VALUE_REQ

OPTIONS = [
    *AUTH,
    OPT_EXPORT_FORMAT,
    click.option(
        "--description",
        "-desc",
        "description",
        help="Description for Set",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    OPT_SET_VALUE_REQ,
    click.option(
        "--append/--no-append",
        "-a/-na",
        "append",
        default=False,
        help="Append supplied value to existing value.",
        show_envvar=True,
        show_default=True,
    ),
]


# XXX NEEDS TESTS
@click.command(name="update-description", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Update the description of a set."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.enforcements.update_description(**kwargs)

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
