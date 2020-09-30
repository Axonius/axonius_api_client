# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import (
    AUTH,
    FIELDS_SELECT,
    QUERY,
    add_options,
    get_option_fields_default,
    get_option_help,
)
from ..grp_common import WIZ, load_wiz
from .grp_common import EXPORT_FORMAT, OVERWRITE, SQ_OPTS, check_sq_exist, handle_export

OPTIONS = [
    *AUTH,
    *SQ_OPTS,
    EXPORT_FORMAT,
    *QUERY,
    *FIELDS_SELECT,
    get_option_fields_default(default=True),
    OVERWRITE,
    *WIZ,
    click.option(
        "--name",
        "-n",
        "name",
        help="Name of saved query",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    get_option_help(choices=["auth", "query", "selectfields", "wizard"]),
]


@click.command(name="add", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, wizard_content, overwrite, **kwargs):
    """Add a saved query."""
    column_filters = kwargs.get("column_filters", [])
    if column_filters:
        kwargs["column_filters"] = dict(kwargs.get("column_filters", []))

    query_file = kwargs.pop("query_file", None)
    if query_file:
        kwargs["query"] = query_file.read().strip()

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)
    name = kwargs["name"]
    check_sq_exist(ctx=ctx, apiobj=apiobj, name=name, overwrite=overwrite)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        kwargs = load_wiz(apiobj=apiobj, wizard_content=wizard_content, exprs=True, kwargs=kwargs)
        row = apiobj.saved_query.add(**kwargs)

    ctx.obj.echo_ok(f"Successfully created saved query: {name}")
    ctx.exit(handle_export(ctx=ctx, rows=row, export_format=export_format))
