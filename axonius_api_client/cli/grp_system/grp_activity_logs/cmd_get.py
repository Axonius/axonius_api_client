# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....api.json_api.audit_logs import AuditLog
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT, handle_export

SEARCH_OPTS = [
    click.option(
        f"--{prop}",
        f"{prop}",
        help=f"Only return records where property {prop!r} matches a regex (multiple)",
        default=None,
        metavar="REGEX",
        type=str,
        show_envvar=True,
        show_default=True,
        required=False,
        multiple=True,
    )
    for prop in AuditLog._search_properties()
]


OPTIONS = [
    *AUTH,
    *EXPORT,
    click.option(
        "--max-rows",
        "max_rows",
        help="Stop fetching assets after this many rows have been received",
        default=None,
        type=click.INT,
        show_envvar=True,
        show_default=True,
        required=False,
        multiple=False,
    ),
    click.option(
        "--start-date",
        "-sd",
        "start_date",
        help="Only return records with dates after this value",
        default=None,
        type=str,
        show_envvar=True,
        show_default=True,
        required=False,
        multiple=False,
    ),
    click.option(
        "--end-date",
        "-ed",
        "end_date",
        help="Only return records with dates before this value",
        default=None,
        type=str,
        show_envvar=True,
        show_default=True,
        required=False,
        multiple=False,
    ),
    click.option(
        "--within-last-hours",
        "-wlh",
        "within_last_hours",
        help="Only return records that happened N hours ago",
        default=None,
        type=click.INT,
        show_envvar=True,
        show_default=True,
        required=False,
        multiple=False,
    ),
    *SEARCH_OPTS,
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get the Activity Logs."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.activity_logs.get(**kwargs)

    handle_export(ctx=ctx, data=data, export_format=export_format, **kwargs)
