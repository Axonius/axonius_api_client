# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....constants import GUI_PAGE_SIZES
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
        click.secho(json_dump(rows))
        ctx.exit(0)

    if export_format == "str-names":
        names = "\n".join([x["name"] for x in listify(rows)])
        click.secho(names)
        ctx.exit(0)

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

        ctx.exit(0)


# def add_handler(ctx, url, key, secret, **kwargs):
#     """Pass."""
#     column_filters = kwargs.get("column_filters", [])
#     if column_filters:
#         kwargs["column_filters"] = dict(kwargs.get("column_filters", []))

#     query_file = kwargs.pop("query_file", None)
#     if query_file:
#         kwargs["query"] = query_file.read().strip()

#     client = ctx.obj.start_client(url=url, key=key, secret=secret)

#     p_grp = ctx.parent.parent.command.name
#     apiobj = getattr(client, p_grp)

#     with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
#         row = apiobj.saved_query.add(**kwargs)

#     msg = "Successfully created saved query: {n}"
#     msg = msg.format(n=row["name"])
#     ctx.obj.echo_ok(msg)
#     click.secho(json_dump(row))
#     ctx.exit(0)


# def del_handler(ctx, url, key, secret, get_method, **kwargs):
#     """Pass."""
#     client = ctx.obj.start_client(url=url, key=key, secret=secret)

#     p_grp = ctx.parent.parent.command.name
#     apiobj = getattr(client, p_grp)
#     get_method = getattr(apiobj.saved_query, get_method)

#     with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
#         rows = listify(get_method(**kwargs))
#         apiobj.saved_query.delete(rows=rows)

#     ctx.obj.echo_ok("Successfully deleted saved queries:")
#     for row in rows:
#         ctx.obj.echo_ok("  {}".format(row["name"]))
#     ctx.exit(0)


# def get_handler(ctx, url, key, secret, method, export_format, **kwargs):
#     """Pass."""
#     client = ctx.obj.start_client(url=url, key=key, secret=secret)

#     method = method.replace("-", "_")
#     p_grp = ctx.parent.parent.command.name
#     apiobj = getattr(client, p_grp)
#     get_method = getattr(apiobj.saved_query, method)

#     with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
#         rows = get_method(**kwargs)

#     handle_export(ctx=ctx, rows=rows, export_format=export_format)


# def get_tags_handler(ctx, url, key, secret, method, **kwargs):
#     """Pass."""
#     client = ctx.obj.start_client(url=url, key=key, secret=secret)

#     method = method.replace("-", "_")
#     p_grp = ctx.parent.parent.command.name
#     apiobj = getattr(client, p_grp)
#     get_method = getattr(apiobj.saved_query, method)

#     with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
#         rows = listify(get_method(**kwargs))

#     ctx.obj.echo_ok("Successfully fetched {} saved query tags".format(len(rows)))
#     click.secho("\n".join(rows))
#     ctx.exit(0)
