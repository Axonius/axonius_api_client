# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....constants.api import GUI_PAGE_SIZES
from ....tools import json_dump, listify
from ...context import SplitEquals, click
from ...options import int_callback

EXPORT_FORMAT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json", "str", "str-names"]),
    help="Format of to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)
OVERWRITE = click.option(
    "--overwrite/--no-overwrite",
    "-ow/-now",
    "overwrite",
    default=False,
    help="Overwrite pre-existing query.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
ABORT = click.option(
    "--abort/--no-abort",
    "-a/-na",
    "abort",
    help="Stop adding saved queries if an error happens",
    required=False,
    default=True,
    show_envvar=True,
    show_default=True,
)
SQ_OPTS = [
    click.option(
        "--tag",
        "-t",
        "tags",
        help="Tags to set for saved query",
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sort-field",
        "-sf",
        "sort_field",
        help="Column to sort data on.",
        metavar="ADAPTER:FIELD",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sort-ascending",
        "-sd",
        "sort_descending",
        default=True,
        help="Sort --sort-field ascending.",
        is_flag=True,
        show_envvar=True,
    ),
    click.option(
        "--column-filter",
        "-cf",
        "column_filters",
        help="Columns to filter in the format of adapter:field=value.",
        metavar="ADAPTER:FIELD=value",
        type=SplitEquals(),
        multiple=True,
        show_envvar=True,
    ),
    click.option(
        "--gui-page-size",
        "-gps",
        default=format(GUI_PAGE_SIZES[0]),
        help="Number of rows to show per page in GUI.",
        type=click.Choice([format(x) for x in GUI_PAGE_SIZES]),
        callback=int_callback,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--description",
        "-d",
        "description",
        help="Description to set on saved query",
        show_envvar=True,
        show_default=True,
        default=None,
    ),
]


def handle_export(ctx, rows, export_format):
    """Pass."""
    if export_format == "json":
        # convert the list into a single item if only one item
        if isinstance(rows, list) and len(rows) == 1:
            rows = rows[0]

        click.secho(json_dump(rows))
        return 0

    if export_format == "str-names":
        names = "\n".join([x["name"] for x in listify(rows)])
        click.secho(names)
        return 0

    if export_format == "str":
        for row in listify(rows):
            name = row["name"]
            description = row.get("description", "")
            query = row["view"].get("query", {}).get("filter", None)

            tags = "\n  " + "\n  ".join(row.get("tags", []))
            fields = "\n  " + "\n  ".join(row["view"].get("fields", []))

            click.secho("\n-----------------------------------------------")
            click.secho(f"Name: {name}")
            click.secho(f"Description: {description}")
            click.secho(f"Query: {query}")
            click.secho(f"Tags: {tags}")
            click.secho(f"Fields: {fields}")

        return 0

    return 1


def check_sq_exist(ctx, apiobj, name, overwrite):
    """Pass."""
    try:
        apiobj.saved_query.get_by_name(value=name)
    except Exception:
        ctx.obj.echo_ok(f"Saved query {name!r} does not exist, will add")
    else:
        if not overwrite:
            ctx.obj.echo_error(f"Saved Query named {name!r} exists and overwrite is False")
        else:
            ctx.obj.echo_ok(f"Saved query {name!r} exists and overwrite is True, will add")
