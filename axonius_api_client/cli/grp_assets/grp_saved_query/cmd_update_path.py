# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, OPTS_REQ_FOLDER, add_options
from .grp_common import EXPORT_FORMATS, OPT_UPDATE_SQ, OPTS_EXPORT

OPTIONS = [
    *AUTH,
    *OPTS_EXPORT,
    OPT_UPDATE_SQ,
    *OPTS_REQ_FOLDER,
]

# XXX TEST


@click.command(name="update-path", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, sq, path, create):
    """Update the path of a Saved Query."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.saved_query.update_path(
            sq=sq, path=path, create=create, echo=True, as_dataclass=True
        )
        ctx.obj.echo_ok(f"Successfully updated Saved Query {data.name}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
