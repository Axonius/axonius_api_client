# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import json_dump, listify
from ..options import click


def add_handler(ctx, url, key, secret, **kwargs):
    """Pass."""
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

    msg = "Successfully created saved query: {n}"
    msg = msg.format(n=row["name"])
    ctx.obj.echo_ok(msg)
    click.secho(json_dump(row))
    ctx.exit(0)


def del_handler(ctx, url, key, secret, get_method, **kwargs):
    """Pass."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)
    get_method = getattr(apiobj.saved_query, get_method)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = listify(get_method(**kwargs))
        apiobj.saved_query.delete(rows=rows)

    ctx.obj.echo_ok("Successfully deleted saved queries:")
    for row in rows:
        ctx.obj.echo_ok("  {}".format(row["name"]))
    ctx.exit(0)


def get_handler(ctx, url, key, secret, method, schema_type, **kwargs):
    """Pass."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    method = method.replace("-", "_")
    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)
    get_method = getattr(apiobj.saved_query, method)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = listify(get_method(**kwargs))

    ctx.obj.echo_ok("Successfully fetched {} saved queries".format(len(rows)))
    if schema_type == "basic":
        for row in rows:
            lines = [
                "name: {}".format(row["name"]),
                "description: {}".format(row["description"]),
                "query: {}".format(row["view"].get("query", {}).get("filter", None)),
                "tags: {}".format(row.get("tags", [])),
                "fields: {}".format(row["view"].get("fields", [])),
                "",
            ]
            lines = "\n  ".join(lines)
            click.secho(lines)
        ctx.exit(0)

    click.secho(json_dump(rows))
    ctx.exit(0)


def get_tags_handler(ctx, url, key, secret, method, **kwargs):
    """Pass."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    method = method.replace("-", "_")
    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)
    get_method = getattr(apiobj.saved_query, method)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = listify(get_method(**kwargs))

    ctx.obj.echo_ok("Successfully fetched {} saved query tags".format(len(rows)))
    click.secho(json_dump(rows))
    ctx.exit(0)
