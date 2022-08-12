# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....api.json_api.paging_state import PagingState
from ....api.json_api.saved_queries import QueryHistory, QueryHistoryRequest, QueryHistorySchema
from ....parsers.tables import tablize
from ....tools import csv_writer, json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options, build_filter_opt


def export_to_tablize(data, **kwargs):
    """Pass."""
    items = [x.to_tablize() for x in data] if isinstance(data, list) else [data.to_tablize()]
    return tablize(items)


def export_csv(data, **kwargs):
    """Pass."""
    rows = [x.to_csv() for x in data]
    columns = QueryHistory._props_csv()
    return csv_writer(rows=rows, columns=columns)


def export_json_full(data, **kwargs):
    """Pass."""
    return json_dump(data)


MAP_EXPORT_FORMATS: dict = {
    "table": export_to_tablize,
    "json": export_json_full,
    "csv": export_csv,
}

OPT_EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(list(MAP_EXPORT_FORMATS)),
    help="Format of to export data in",
    default=list(MAP_EXPORT_FORMATS)[0],
    show_envvar=True,
    show_default=True,
)

OPT_START_DT = click.option(
    "--date-start",
    "-ds",
    "date_start",
    help="Filter records that are after this date.",
    default=None,
    metavar="DATE",
    show_envvar=True,
    show_default=True,
    required=False,
)
OPT_END_DT = click.option(
    "--date-end",
    "-de",
    "date_end",
    help="Filter records that are before this date. (defaults to now if start but no end)",
    default=None,
    metavar="DATE",
    show_envvar=True,
    show_default=True,
    required=False,
)
OPT_NAME_TERM = click.option(
    "--name-term",
    "-nt",
    "name_term",
    help="Filter records that match this Saved Query name pattern",
    default=None,
    show_envvar=True,
    show_default=True,
    required=False,
)

OPT_SORT_ATTR = click.option(
    "--sort-attribute",
    "-sa",
    "sort_attribute",
    help="Sort records based on this attribute",
    default=None,
    type=click.Choice(list(QueryHistorySchema.validate_attrs())),
    show_envvar=True,
    show_default=True,
    required=False,
)
OPT_SORT_DESC = click.option(
    "--sort-descending/--no-sort-descending",
    "-sd/-nsd",
    "sort_descending",
    default=False,
    help="Sort --sort-attribute descending or ascending.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
    required=False,
)

OPT_PAGE_SLEEP = click.option(
    "--page-sleep",
    "-psl",
    "page_sleep",
    default=PagingState.page_sleep,
    help="Sleep N seconds between pages.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
OPT_PAGE_SIZE = click.option(
    "--page-size",
    "-psz",
    "page_size",
    default=PagingState.page_size,
    help="Get N records per page.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
OPT_ROW_START = click.option(
    "--row-start",
    "-prt",
    "row_start",
    default=PagingState.row_start,
    help="Start at row N.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
OPT_ROW_STOP = click.option(
    "--row-stop",
    "-prp",
    "row_stop",
    default=PagingState.row_stop,
    help="Stop at row N.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)

OPTS_FILTERS = [build_filter_opt(value_type=x) for x in QueryHistoryRequest.get_list_props()]
OPTS_TIME_RANGE = [
    OPT_START_DT,
    OPT_END_DT,
]
OPTS_SORT = [
    OPT_SORT_ATTR,
    OPT_SORT_DESC,
]
OPTS_PAGING = [
    OPT_PAGE_SLEEP,
    OPT_PAGE_SIZE,
    OPT_ROW_START,
    OPT_ROW_STOP,
]
OPTIONS = [
    *AUTH,
    *OPTS_PAGING,
    *OPTS_FILTERS,
    *OPTS_TIME_RANGE,
    *OPTS_SORT,
    OPT_NAME_TERM,
    OPT_EXPORT,
]


@click.command(name="get-query-history", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get query history events."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.saved_query.get_query_history(**kwargs)
        ctx.obj.echo_ok(f"Received {len(data)} Query History Events")

    click.secho(MAP_EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
