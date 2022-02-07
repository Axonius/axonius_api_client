# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import (
    EXPORT_FORMATS,
    OPT_UPDATE_APPEND,
    OPT_UPDATE_REMOVE,
    OPT_UPDATE_SQ,
    OPTS_EXPORT,
)

OPTIONS = [
    *AUTH,
    *OPTS_EXPORT,
    OPT_UPDATE_SQ,
    click.option(
        "--value",
        "-v",
        "value",
        help="Value to update (multiples)",
        multiple=True,
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    OPT_UPDATE_APPEND,
    OPT_UPDATE_REMOVE,
]


@click.command(name="update-tags", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, sq, value, append, remove):
    """Update the tags of a Saved Query."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.saved_query.update_tags(
            sq=sq, value=value, append=append, remove=remove, as_dataclass=True
        )
        ctx.obj.echo_ok(f"Successfully updated Saved Query {data.name}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
