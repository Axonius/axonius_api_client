# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import tabulate

from ...constants import FIELD_JOINER, FIELD_TRIM_LEN, TABLE_FORMAT, TABLE_MAX_ROWS
from ..context import CONTEXT_SETTINGS, click
from ..options import (
    AUTH,
    EXPORT,
    FIELDS_SELECT,
    PAGING,
    add_options,
    get_option_fields_default,
    get_option_help,
)

HISTORY_DATE = click.option(
    "--history-date",
    "-hd",
    "history_date",
    default=None,
    help="Return results for a given date in history",
    show_envvar=True,
    show_default=True,
    hidden=False,
    metavar="YYYY-MM-DD",
)

GET_EXPORT = [
    click.option(
        "--use-cursor/--no-use-cursor",
        "use_cursor",
        default=True,
        help="Use cursor for pagination",
        hidden=True,
    ),
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
        default=10000,
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
        type=click.Choice(["csv", "json", "table", "json_to_csv", "xlsx"]),
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--table-format",
        "table_format",
        default=TABLE_FORMAT,
        help="Table format to use for --export-format=table",
        type=click.Choice(tabulate.tabulate_formats),
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--table-max-rows",
        "table_max_rows",
        default=TABLE_MAX_ROWS,
        help="Only return this many rows for --export-format=table",
        show_envvar=True,
        show_default=True,
        type=click.INT,
        hidden=False,
    ),
    click.option(
        "--table-api-fields/--no-table-api-fields",
        "table_api_fields",
        default=False,
        help="Include API related fields in table output",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--schema/--no-schema",
        "export_schema",
        default=False,
        help="Add schema information to the export",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--json-flat/--no-json-flat",
        "json_flat",
        default=False,
        help="Flat JSON output (one line per row)",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--titles/--no-titles",
        "field_titles",
        default=None,
        help="Rename fields from internal field names to their column titles",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--join/--no-join",
        "field_join",
        default=None,
        help="Join multivalue fields using --join-value",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--join-value",
        "field_join_value",
        default=FIELD_JOINER,
        help="Value to use for joining multivalue fields, default: \\n",
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--join-trim",
        "field_join_trim",
        default=FIELD_TRIM_LEN,
        help="Character length to trim joined multivalue fields",
        show_envvar=True,
        show_default=True,
        type=click.INT,
        hidden=False,
    ),
    click.option(
        "--explode",
        "field_explode",
        default="",
        help="Flatten and explode a fields values into multiple rows",
        show_envvar=True,
        show_default=True,
        hidden=False,
        metavar="FIELD",
    ),
    click.option(
        "--flatten/--no-flatten",
        "field_flatten",
        default=None,
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
        default=[],
        show_envvar=True,
        show_default=True,
        hidden=False,
        metavar="FIELD",
    ),
    click.option(
        "--field-null/--no-field-null",
        "field_null",
        default=None,
        help="Add missing fields with --field-null-value",
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
    click.option(
        "--field-null-value",
        "field_null_value",
        default=None,
        help="Value to use for fields that are not returned",
        show_envvar=True,
        show_default=True,
        hidden=False,
    ),
    click.option(
        "--adapters-missing/--no-adapters-missing",
        "report_adapters_missing",
        default=False,
        help="Add a column showing adapters missing from each asset",
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
        default=[],
        show_envvar=True,
        show_default=True,
        hidden=False,
        metavar="TAG",
    ),
    click.option(
        "--untag",
        "tags_remove",
        help="Tags to remove from each asset (multiples)",
        multiple=True,
        default=[],
        show_envvar=True,
        show_default=True,
        hidden=False,
        metavar="TAG",
    ),
    click.option(
        "--include-details/--no-include-details",
        "-id/-nid",
        "include_details",
        help="Include details for aggregated fields (req: 3.4 + patch)",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sort-descending/--no-sort-descending",
        "-sd/-nsd",
        "sort_descending",
        help="Sort --sort-field descending (req: 3.4 + patch)",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sort-field",
        "-sf",
        "sort_field",
        help="Sort assets based on a specific field (req: 3.4 + patch)",
        default=None,
        show_envvar=True,
        show_default=True,
    ),
    HISTORY_DATE,
]
# XXX show historical dates

GET_BUILDERS = [
    *AUTH,
    *PAGING,
    *EXPORT,
    *GET_EXPORT,
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
    if fh:
        return [x.strip() for x in fh.readlines() if x.strip()]
    return None


def gen_get_by_cmd(options, doc, cmd_name, method):
    """Pass."""

    @click.command(name=cmd_name, context_settings=CONTEXT_SETTINGS, help=doc)
    @add_options(options)
    @click.pass_context
    def cmd(ctx, url, key, secret, whitelist=None, get_method=method, **kwargs):
        client = ctx.obj.start_client(url=url, key=key, secret=secret)
        kwargs["report_software_whitelist"] = load_whitelist(whitelist)

        p_grp = ctx.parent.command.name
        apiobj = getattr(client, p_grp)
        apimethod = getattr(apiobj, get_method)

        with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
            apimethod(**kwargs)

    cmd.__doc__ = doc
    return cmd
