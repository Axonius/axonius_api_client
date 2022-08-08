# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...api.json_api.adapters import AdapterFetchHistoryFilters, AdapterFetchHistorySchema
from ...api.json_api.paging_state import PagingState
from ...api.json_api.time_range import UnitTypes
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import export_csv, export_json_full, export_to_tablize


def build_filter_opt(value_type: str):
    """Pass."""
    short_opt = "".join([x[0] for x in value_type.split("_")])
    camel = " ".join(x.title() for x in value_type.split("_"))
    return click.option(
        f"--filter-{value_type}",
        f"-f{short_opt}",
        f"{value_type}",
        help=f"Filter for records with matching {camel} (~ prefix for regex!) (multiple)",
        multiple=True,
        show_envvar=True,
        show_default=True,
        required=False,
    )


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

OPT_REALTIME = click.option(
    "--exclude-realtime/--no-exclude-realtime",
    "-er/-ner",
    "exclude_realtime",
    default=False,
    help="Exclude records for realtime adapters.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
    required=False,
)

OPT_REL_UNIT_TYPE = click.option(
    "--relative-unit-type",
    "-rut",
    "relative_unit_type",
    default=UnitTypes.get_default(),
    help="Type of unit to use when supplying --relative-unit-count.",
    type=click.Choice(UnitTypes.keys()),
    show_envvar=True,
    show_default=True,
    required=False,
)
OPT_REL_UNIT_COUNT = click.option(
    "--relative-unit-count",
    "-ruc",
    "absolute_date_start",
    help="Filter records for the past N units of --relative-unit-type.",
    default=None,
    type=click.IntRange(min=1),
    show_envvar=True,
    show_default=True,
    required=False,
)
OPT_ABS_START_DT = click.option(
    "--absolute-date-start",
    "-ads",
    "absolute_date_start",
    help="Filter records that are after this date. (overrides relative values)",
    default=None,
    metavar="DATE",
    show_envvar=True,
    show_default=True,
    required=False,
)
OPT_ABS_END_DT = click.option(
    "--absolute-date-end",
    "-ade",
    "absolute_date_end",
    help="Filter records that are before this date. (defaults to now if start but no end)",
    default=None,
    metavar="DATE",
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
    type=click.Choice(list(AdapterFetchHistorySchema.validate_attrs())),
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

OPTS_FILTERS = [build_filter_opt(value_type=x) for x in AdapterFetchHistoryFilters.value_types()]
OPTS_TIME_RANGE = [
    OPT_REL_UNIT_TYPE,
    OPT_REL_UNIT_COUNT,
    OPT_ABS_START_DT,
    OPT_ABS_END_DT,
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
    OPT_REALTIME,
    *OPTS_TIME_RANGE,
    *OPTS_SORT,
    OPT_EXPORT,
]


@click.command(name="get-fetch-history", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get adapter fetch history events."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.adapters.get_fetch_history(**kwargs)
        ctx.obj.echo_ok(f"Received {len(data)} Fetch History Events")

    click.secho(MAP_EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
