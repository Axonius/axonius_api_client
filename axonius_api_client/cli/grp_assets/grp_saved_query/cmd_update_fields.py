# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, FIELDS_SELECT_BASE, add_options, get_option_fields_default
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
    *FIELDS_SELECT_BASE,
    get_option_fields_default(default=False),
    OPT_UPDATE_APPEND,
    OPT_UPDATE_REMOVE,
]


@click.command(name="update-fields", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, sq, append, remove, **kwargs):
    """Update the fields of a Saved Query."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.saved_query.update_fields(
            sq=sq, append=append, remove=remove, as_dataclass=True, **kwargs
        )
        fields = "\n".join(data.fields)
        ctx.obj.echo_ok(f"Successfully updated Saved Query {data.name}, new fields:\n{fields}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
