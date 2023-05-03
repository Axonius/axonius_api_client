# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ... import DEFAULT_PATH
from ...api import asset_callbacks
from ...api.asset_callbacks.base import ARG_DESCRIPTIONS
from ...constants.asset_helpers import ASSETS_HELPERS
from ...constants.wizards import Results, Types
from ...tools import echo_error, path_read
from ..context import CONTEXT_SETTINGS, SplitEquals, click
from ..options import (
    AUTH,
    FIELDS_SELECT,
    OPT_EXPORT_BACKUP,
    OPT_EXPORT_OVERWRITE,
    PAGING,
    TABLE_FMT,
    add_options,
    get_option_fields_default,
    get_option_help,
)

TEMPLATES = "(supports templating: {DATE}, {HISTORY_DATE})"
OPT_EXPORT_FILE = click.option(
    "--export-file",
    "-xf",
    "export_file",
    default="",
    help=f"File to save data to {TEMPLATES}",
    show_envvar=True,
    show_default=True,
    metavar="PATH",
)
OPT_EXPORT_PATH = click.option(
    "--export-path",
    "-xp",
    "export_path",
    default=DEFAULT_PATH,
    help=f"If --export-file supplied, the directory to write --export_file to {TEMPLATES}",
    type=click.Path(exists=False, resolve_path=True),
    show_envvar=True,
    show_default=True,
)
OPTS_EXPORT = [OPT_EXPORT_FILE, OPT_EXPORT_PATH, OPT_EXPORT_OVERWRITE, OPT_EXPORT_BACKUP]
OPT_INCLUDE_FIELDS = click.option(
    "--include-fields/--no-include-fields",
    "-if/-nif",
    "include_fields",
    default=True,
    help=f"Include fields from the saved query {ASSETS_HELPERS.fields.to_str_short()}",
    show_envvar=True,
    show_default=True,
)
OPT_INCLUDE_EXCLUDED_ADAPTERS = click.option(
    "--include-excluded-adapters/--no-include-excluded-adapters",
    "-iea/-niea",
    "include_exclude_adapters",
    default=True,
    help=(
        "Include column filters for excluded adapters from the saved query"
        f" {ASSETS_HELPERS.excluded_adapters.to_str_short()}"
    ),
    show_envvar=True,
    show_default=True,
)
OPT_INCLUDE_ASSET_EXCLUDED_ADAPTERS = click.option(
    "--include-asset-excluded-adapters/--no-include-asset-excluded-adapters",
    "-iaea/-niaea",
    "include_asset_exclude_adapters",
    default=True,
    help=(
        "Include column filters for asset excluded adapters fields from the saved query"
        f" {ASSETS_HELPERS.excluded_adapters.to_str_short()}"
    ),
    show_envvar=True,
    show_default=True,
)
OPT_INCLUDE_FIELD_FILTERS = click.option(
    "--include-field-filters/--no-include-field-filters",
    "-iff/-niff",
    "include_field_filters",
    default=True,
    help=(
        "Include column filters for field filters from the saved query"
        f" {ASSETS_HELPERS.field_filters.to_str_short()}"
    ),
    show_envvar=True,
    show_default=True,
)
OPT_INCLUDE_ASSET_FILTERS = click.option(
    "--include-asset-filters/--no-include-asset-filters",
    "-iaf/-niaf",
    "include_asset_filters",
    default=True,
    help=(
        "Include column filters for asset filters from the saved query"
        f" {ASSETS_HELPERS.asset_filters.to_str_short()}"
    ),
    show_envvar=True,
    show_default=True,
)
OPT_USE_CACHE_ENTRY = click.option(
    "--use-cache-entry/--no-use-cache-entry",
    "-uce/-nuce",
    "use_cache_entry",
    default=False,
    help="Ask the API to use a cache entry for this query, if available",
    show_envvar=True,
    show_default=True,
)
OPT_USE_HEAVY_FIELDS_COLLECTION = click.option(
    "--use-heavy-fields-collection/--no-use-heavy-fields-collection",
    "-uhfc/-nuhfc",
    "use_heavy_fields_collection",
    default=False,
    help="Ask the API to use a heavy fields collection for this query",
    show_envvar=True,
    show_default=True,
)


OPTS_GET_BY_SQ = [
    OPT_INCLUDE_FIELDS,
    OPT_INCLUDE_EXCLUDED_ADAPTERS,
    OPT_INCLUDE_ASSET_EXCLUDED_ADAPTERS,
    OPT_INCLUDE_FIELD_FILTERS,
    OPT_INCLUDE_ASSET_FILTERS,
    OPT_USE_CACHE_ENTRY,
]

HISTORY = [
    click.option(
        "--history-date",
        "-hd",
        "history_date",
        default=None,
        help="Return results for a given date in history",
        show_envvar=True,
        show_default=True,
        hidden=False,
        metavar="YYYY-MM-DD",
    ),
    click.option(
        "--history-days-ago",
        "-hda",
        "history_days_ago",
        default=None,
        help="Return results for a history snapshot N days ago",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--history-exact/--no-history-exact",
        "-hex/-nhex",
        "history_exact",
        default=False,
        help="Date supplied in history-date or history-days-ago is an exact date",
        show_envvar=True,
        show_default=True,
    ),
]


def wiz_callback(ctx, param, value):
    """Pass."""
    contents = []
    if value:
        for i in value:
            etype = i[0].strip().lower()
            if etype not in Types.CLI:
                types = ", ".join(Types.CLI)
                echo_error(msg=f"Invalid expression type {etype!r}, valid types: {types}")
            expr = i[1]
            if etype == Types.FILE:
                contents += path_read(obj=expr)[1].strip().splitlines()
            elif etype == Types.LINES:
                contents += expr.strip().splitlines()
            else:
                contents.append(f"{etype} {expr}")
    return "\n".join(contents)


WIZ = [
    click.option(
        "--wiz",
        "-wz",
        "wizard_content",
        help=(
            "Build a query using an expression (multiples, will override --query). "
            '--wiz "file" "<token>" - Read expressions from a file. '
            '--wiz "lines" "simple expr1<CR>simple expr2" - Read multiple '
            "expressions from a string. "
            '--wiz "simple" "<expr>" - Simple expression. '
            '--wiz "complex" "<expr>" - Complex expression. '
        ),
        nargs=2,
        multiple=True,
        default=[],
        show_envvar=True,
        hidden=False,
        callback=wiz_callback,
        metavar=f'"{"|".join(Types.CLI)}" "EXPRESSION"',
    ),
]
OPTS_GET_API = [
    # 2023-04-22
    click.option(
        "--api-null-for-non-exist/--no-api-null-for-non-exist",
        "-anfne/-nanfne",
        "null_for_non_exist",
        help="Ask the REST API to return null for non existent fields",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--api-filter-out-non-existing-fields/--no-api-filter-out-non-existing-fields",
        "-afonef/-nafonef",
        "filter_out_non_existing_fields",
        help="Ask the REST API to filter out non existent fields",
        is_flag=True,
        default=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--api-max-field-items",
        "-amfi",
        "max_field_items",
        help="Ask the REST API to limit the number of values returned for a field",
        default=None,
        show_envvar=True,
        show_default=True,
        type=click.INT,
    ),
    click.option(
        "--api-complex-fields-preview-limit",
        "-amcfi",
        "complex_fields_preview_limit",
        help="Ask the REST API to limit the number of values returned for a complex field",
        default=None,
        show_envvar=True,
        show_default=True,
        type=click.INT,
    ),
    click.option(
        "--api-use-heavy-fields-collection/--no-api-use-heavy-fields-collection",
        "-ahfc/-nahfc",
        "use_heavy_fields_collection",
        help="Ask the REST API to use the heavy fields collection",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
]
GET_EXPORT = [
    click.option(
        "--echo/--no-echo",
        "do_echo",
        default=True,
        help="Print out details during fetch",
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--page-progress",
        "page_progress",
        default=asset_callbacks.Base.args_map()["page_progress"],
        help="Print progress every N rows",
        show_envvar=True,
        show_default=True,
        type=click.INT,
        hidden=False,
    ),
    click.option(
        "--export-format",
        "-xt",
        "export",
        default="json",
        help="Formatter to use when exporting asset data",
        type=click.Choice([x for x in asset_callbacks.CB_MAP if x not in ["base"]]),
        show_envvar=True,
        show_default=True,
    ),
    TABLE_FMT,
    click.option(
        "--table-max-rows",
        "table_max_rows",
        default=asset_callbacks.Table.args_map()["table_max_rows"],
        help="Only return this many rows for --export-format=table",
        show_envvar=True,
        show_default=True,
        type=click.INT,
        hidden=False,
    ),
    click.option(
        "--table-api-fields/--no-table-api-fields",
        "table_api_fields",
        default=asset_callbacks.Table.args_map()["table_api_fields"],
        help="Include API related fields in table output",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--schema/--no-schema",
        "export_schema",
        default=asset_callbacks.Json.args_map()["export_schema"],
        help="Add schema information to the export",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--json-flat/--no-json-flat",
        "json_flat",
        default=asset_callbacks.Json.args_map()["json_flat"],
        help="Flat JSON output (one line per row)",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--titles/--no-titles",
        "field_titles",
        default=asset_callbacks.Base.args_map()["field_titles"],
        help="Rename fields from internal field names to their column titles",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--field-compress/--no-field-compress",
        "field_compress",
        default=asset_callbacks.Base.args_map()["field_compress"],
        help="Compress field names",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--field-replace",
        "field_replace",
        default=asset_callbacks.Base.args_map()["field_replace"],
        help="Replace characters in field names ex: 'text=replace' (multiples)",
        type=SplitEquals(),
        is_flag=False,
        multiple=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--join/--no-join",
        "field_join",
        default=asset_callbacks.Base.args_map()["field_join"],
        help="Join multivalue fields using --join-value",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--join-value",
        "field_join_value",
        default=asset_callbacks.Base.args_map()["field_join_value"],
        help="Value to use for joining multivalue fields, default: \\n",
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--join-trim",
        "field_join_trim",
        default=asset_callbacks.Base.args_map()["field_join_trim"],
        help="Character length to trim joined multivalue fields",
        show_envvar=True,
        show_default=True,
        type=click.INT,
        hidden=False,
    ),
    click.option(
        "--explode",
        "-exf",
        "field_explode",
        default=asset_callbacks.Base.args_map()["field_explode"],
        help="Flatten and explode a fields values into multiple rows",
        show_envvar=True,
        show_default=True,
        hidden=False,
        metavar="FIELD",
    ),
    click.option(
        "--explode_entities/--no-explode_entities",
        "--explode-entities/--no-explode-entities",
        "-exe/-nexe",
        "explode_entities",
        default=asset_callbacks.Base.args_map()["explode_entities"],
        help="Split rows into one row for each asset entity (will enable include-details)",
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--flatten/--no-flatten",
        "field_flatten",
        default=asset_callbacks.Base.args_map()["field_flatten"],
        help="Remove complex fields and re-add their sub-field values to the row",
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--field-exclude",
        "-fx",
        "field_excludes",
        help="Fields to exclude from each row (multiples)",
        multiple=True,
        default=asset_callbacks.Base.args_map()["field_excludes"],
        show_envvar=True,
        show_default=True,
        hidden=False,
        metavar="FIELD",
    ),
    click.option(
        "--field-null/--no-field-null",
        "field_null",
        default=asset_callbacks.Base.args_map()["field_null"],
        help="Add missing fields with --field-null-value",
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--field-null-value",
        "field_null_value",
        default=asset_callbacks.Base.args_map()["field_null_value"],
        help="Value to use for fields that are not returned",
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--adapters-missing/--no-adapters-missing",
        "report_adapters_missing",
        default=asset_callbacks.Base.args_map()["report_adapters_missing"],
        help="Add a column showing adapters missing from each asset",
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--include-dates/--no-include-dates",
        "include_dates",
        default=asset_callbacks.Base.args_map()["include_dates"],
        help="Include history date and current date as columns in each asset",
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--software-whitelist-file",
        "whitelist",
        default=None,
        help="Read in a file of software names to add missing and delta sw columns",
        show_envvar=True,
        show_default=True,
        type=click.File(),
    ),
    click.option(
        "--tag",
        "tags_add",
        help="Tags to add to each asset (multiples)",
        multiple=True,
        default=asset_callbacks.Base.args_map()["tags_add"],
        show_envvar=True,
        show_default=True,
        hidden=False,
        metavar="TAG",
    ),
    click.option(
        "--tag-invert/--no-tag-invert",
        "tags_add_invert_selection",
        default=asset_callbacks.Base.args_map()["tags_add_invert_selection"],
        help="Only add tags to assets that do NOT match the query provided",
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--untag",
        "tags_remove",
        help="Tags to remove from each asset (multiples)",
        multiple=True,
        default=asset_callbacks.Base.args_map()["tags_remove"],
        show_envvar=True,
        show_default=True,
        hidden=False,
        metavar="TAG",
    ),
    click.option(
        "--untag-invert/--no-untag-invert",
        "tags_remove_invert_selection",
        default=asset_callbacks.Base.args_map()["tags_remove_invert_selection"],
        help="Only remove tags from assets that do NOT match the query provided",
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--include-details/--no-include-details",
        "-id/-nid",
        "include_details",
        help="Include details for aggregated fields",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sort-descending/--no-sort-descending",
        "-sd/-nsd",
        "sort_descending",
        help="Sort --sort-field descending",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sort-field",
        "-sf",
        "sort_field",
        help="Sort assets based on a specific field",
        default=None,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--csv-field-flatten/--no-csv-field-flatten",
        "csv_field_flatten",
        default=asset_callbacks.Csv.args_map()["csv_field_flatten"],
        help=ARG_DESCRIPTIONS["csv_field_flatten"],
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--csv-field-join/--no-csv-field-join",
        "csv_field_join",
        default=asset_callbacks.Csv.args_map()["csv_field_join"],
        help=ARG_DESCRIPTIONS["csv_field_join"],
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--csv-field-null/--no-csv-field-null",
        "csv_field_null",
        default=asset_callbacks.Csv.args_map()["csv_field_null"],
        help=ARG_DESCRIPTIONS["csv_field_null"],
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    *OPTS_GET_API,
]

GET_BUILDERS = [
    *AUTH,
    *PAGING,
    *OPTS_EXPORT,
    *GET_EXPORT,
    *HISTORY,
    *FIELDS_SELECT,
    get_option_fields_default(default=True),
    click.option(
        "--pre",
        "pre",
        help="Query to prefix the query built to search for --value",
        default="",
        metavar="QUERY",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--post",
        "post",
        help="Query to postfix the query built to search for --value",
        default="",
        metavar="QUERY",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--not-flag/--no-not-flag",
        "-nf/-nnf",
        "not_flag",
        help="Build the query as a NOT query",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
]

GET_BY_VALUE_BUILDERS = [
    *GET_BUILDERS,
    click.option(
        "--value",
        "-v",
        "value",
        help="Value to search for",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    get_option_help(choices=["auth", "assetexport", "selectfields"]),
]

GET_BY_VALUES_BUILDERS = [
    *GET_BUILDERS,
    click.option(
        "--value",
        "-v",
        "values",
        help="Values to search for (multiples)",
        required=True,
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
    get_option_help(choices=["auth", "assetexport", "selectfields"]),
]

GET_BY_VALUE_REGEX_BUILDERS = [
    *GET_BUILDERS,
    click.option(
        "--value",
        "-v",
        "value",
        help="Regular expression value to search for",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--case-in-sensitive/--case-sensitive",
        "-cis/-cs",
        "cast_insensitive",
        help="Build a regex that is / is not cases sensitive",
        is_flag=True,
        default=True,
        show_envvar=True,
        show_default=True,
    ),
    get_option_help(choices=["auth", "assetexport", "selectfields"]),
]

GET_BY_VALUE_FIELD = click.option(
    "--field",
    "-f",
    "field",
    help="Field to use when building the query",
    required=True,
    show_envvar=True,
    show_default=True,
)


def load_whitelist(fh):
    """Pass."""
    return [x.strip() for x in fh.readlines() if x.strip()] if fh else None


def gen_get_by_cmd(options, doc, cmd_name, method):
    """Pass."""

    @click.command(name=cmd_name, context_settings=CONTEXT_SETTINGS, help=doc)
    @add_options(options)
    @click.pass_context
    def cmd(ctx, url, key, secret, whitelist=None, get_method=method, **kwargs):
        ctx.obj.echo_warn(
            (
                "This command is deprecated and will be removed in the next major version"
                "- Use get with --wiz instead!)"
            )
        )
        client = ctx.obj.start_client(url=url, key=key, secret=secret)
        kwargs["report_software_whitelist"] = load_whitelist(whitelist)
        p_grp = ctx.parent.command.name
        apiobj = getattr(client, p_grp)
        apimethod = getattr(apiobj, get_method)
        with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
            apimethod(**kwargs)

    cmd.__doc__ = doc
    return cmd


def load_wiz(apiobj, wizard_content, kwargs, wizard_file=None, exprs=False):
    """Pass."""
    result = None
    if wizard_file:
        result = apiobj.wizard_file.parse_path(path=wizard_file)
    if wizard_content:
        result = apiobj.wizard_text.parse(content=wizard_content)
    if result:
        query = result[Results.QUERY]
        click.secho(f"Wizard built a query: {query}", err=True, fg="green")
        kwargs["query"] = query
        if exprs:
            kwargs["expressions"] = result[Results.EXPRS]
    return kwargs
