# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import listify
from ..options import click


def handler(ctx, url, key, secret, method, rows=None, **kwargs):
    """Handle all of the get* commands."""
    action_map = {
        "add": "Added labels {labels} to {cnt} {atype}",
        "remove": "Removed labels {labels} from {cnt} {atype}",
    }

    labels = kwargs.get("labels", [])
    p_grp = ctx.parent.parent.command.name
    method = method.replace("-", "_")
    echo = True

    if method in action_map:
        kwargs["rows"] = rows = ctx.obj.read_stream_rows(
            stream=rows, this_cmd="{} labels {}".format(p_grp, method)
        )

        rows = listify(rows)
        req_key = "internal_axon_id"
        if not rows:
            ctx.obj.echo_error("Empty rows supplied: {}".format(rows))

        for row in rows:
            if not isinstance(row, dict):
                ctx.obj.echo_error("Supplied row {} is not a dictionary".format(row))
            if not row.get(req_key):
                ctx.obj.echo_error(
                    "Supplied row {} does not have key {} ".format(row, req_key)
                )

        echo = False

    client = ctx.obj.start_client(url=url, key=key, secret=secret, echo=echo)
    apiobj = getattr(client, p_grp)
    apiobj_child = getattr(apiobj, "labels")
    apimethod = getattr(apiobj_child, method)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_data = apimethod(**kwargs)

    if method in action_map:
        ctx.obj.echo_ok(
            action_map[method].format(labels=labels, cnt=raw_data, atype=p_grp)
        )
        ctx.exit(0)

    ctx.obj.echo_ok("Received {} labels".format(len(raw_data)))
    click.secho("\n".join(raw_data))
    ctx.exit(0)
