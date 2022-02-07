# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, QUERY, add_options
from ..grp_common import WIZ, load_wiz
from .grp_common import EXPORT_FORMATS, OPT_UPDATE_APPEND, OPT_UPDATE_SQ, OPTS_EXPORT

OPTIONS = [
    *AUTH,
    *OPTS_EXPORT,
    *QUERY,
    *WIZ,
    OPT_UPDATE_SQ,
    OPT_UPDATE_APPEND,
    click.option(
        "--append-and-flag/--no-append-and-flag",
        "-aaf/-naaf",
        "append_and_flag",
        default=False,
        help="Append supplied query using 'and' instead of 'or'.",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--append-not-flag/--no-append-not-flag",
        "-anf/-nanf",
        "append_not_flag",
        default=False,
        help="Append supplied query using 'not'.",
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="update-query", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, sq, wizard_content, **kwargs):
    """Update the query of a Saved Query."""
    query_file = kwargs.pop("query_file", None)
    kwargs["query"] = query_file.read().strip() if query_file else kwargs.get("query")
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        kwargs = load_wiz(apiobj=apiobj, wizard_content=wizard_content, exprs=True, kwargs=kwargs)
        data = apiobj.saved_query.update_query(sq=sq, as_dataclass=True, **kwargs)
        ctx.obj.echo_ok(f"Successfully updated Saved Query {data.name}, new query:\n{data.query}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
