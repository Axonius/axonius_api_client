# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import NotFoundError
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, INPUT_FILE, add_options

OPTIONS = [*AUTH, INPUT_FILE]


@click.command(name="add-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file, **kwargs):
    """Add a saved query from a JSON file."""
    new_sq = ctx.obj.read_stream_json(stream=input_file, expect=dict)

    remove_keys = [
        "date_fetched",
        "predefined",
        "timestamp",
        "updated_by",
        "user_id",
        "uuid",
    ]
    [new_sq.pop(x, None) for x in remove_keys]

    set_defaults = {"query_type": "saved"}
    new_sq.update(set_defaults)

    ensure_keys = ["name", "view"]
    missing_keys = [x for x in ensure_keys if x not in new_sq]

    if missing_keys:
        missing_keys = ", ".join(missing_keys)
        ctx.obj.echo_error(f"Missing required keys: {missing_keys}")

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    sq_name = new_sq["name"]

    try:
        row = apiobj.saved_query.get_by_name(value=sq_name)
        ctx.obj.echo_error(f"Saved query {sq_name!r} already exists, can not add")
    except NotFoundError:
        ctx.obj.echo_ok(f"Saved query {sq_name!r} does not exist, will add")

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        sq_uuid = apiobj.saved_query._add(data=new_sq)
        row = apiobj.saved_query.get_by_uuid(value=sq_uuid)

    ctx.obj.echo_ok(f"Successfully created saved query: {row['name']}")

    click.secho(json_dump(row))

    ctx.exit(0)
