# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, FIELDS_SELECT, QUERY, add_options, get_option_fields_default
from .grp_common import SQ_OPTS

EPILOG = """Note:

Creating a saved query using this method will not create a proper set of
expressions, which will mean the query wizard will not show the filter lines
for the supplied query!
"""

OPTIONS = [
    *AUTH,
    *QUERY,
    *FIELDS_SELECT,
    get_option_fields_default(default=False),
    *SQ_OPTS,
    click.option(
        "--name",
        "-n",
        "name",
        help="Name of saved query",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="add", context_settings=CONTEXT_SETTINGS, epilog=EPILOG)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
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

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        row = apiobj.saved_query.add(**kwargs)

    ctx.obj.echo_ok(f"Successfully created saved query: {row['name']}")

    click.secho(json_dump(row))

    ctx.exit(0)
