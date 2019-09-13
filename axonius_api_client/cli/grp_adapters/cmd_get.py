# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pdb  # noqa

import click

from ... import tools
from .. import context


@click.command("get", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--name",
    help="Only include adapters with matching names.",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--node",
    help="Only include adapters with matching node names.",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cnx-working/--no-cnx-working",
    help="Include/Exclude adapters with working connections.",
    is_flag=True,
    default=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cnx-broken/--no-cnx-broken",
    help="Include/Exclude adapters with broken connections.",
    is_flag=True,
    default=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cnx-none/--no-cnx-none",
    help="Include/Exclude adapters with no connections.",
    default=True,
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--cnx-count",
    help="Only include adapters with this number of connections.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--include-settings/--no-include-settings",
    help="Include connection, adapter, and advanced setitngs in CSV export.",
    default=False,
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@context.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    export_format,
    export_file,
    export_path,
    export_overwrite,
    name,
    node,
    cnx_working,
    cnx_broken,
    cnx_none,
    cnx_count,
    include_settings,
):
    """Get all adapters with clients that have errors."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    statuses = []

    if cnx_working:
        statuses.append(True)

    if cnx_broken:
        statuses.append(False)

    if cnx_none:
        statuses.append(None)

    with context.exc_wrap(wraperror=ctx.wraperror):
        all_adapters = client.adapters.get()

        by_nodes = client.adapters.filter_by_nodes(adapters=all_adapters, value=node)
        check_empty(
            ctx=ctx,
            this_data=by_nodes,
            prev_data=all_adapters,
            value_type="node names",
            value=node,
        )

        by_names = client.adapters.filter_by_names(adapters=by_nodes, value=name)
        check_empty(
            ctx=ctx,
            this_data=by_names,
            prev_data=by_nodes,
            value_type="names",
            value=name,
        )

        by_statuses = client.adapters.filter_by_status(
            adapters=by_names, value=statuses
        )
        check_empty(
            ctx=ctx,
            this_data=by_statuses,
            prev_data=by_names,
            value_type="statuses",
            value=[format(x) for x in statuses],
        )

        by_cnx_count = client.adapters.filter_by_cnx_count(
            adapters=by_names, value=cnx_count
        )
        check_empty(
            ctx=ctx,
            this_data=by_cnx_count,
            prev_data=by_statuses,
            value_type="connection count",
            value=cnx_count,
        )

    formatters = {"json": to_json, "csv": to_csv}
    ctx.handle_export(
        raw_data=by_cnx_count,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        include_settings=include_settings,
    )


def check_empty(ctx, this_data, prev_data, value_type, value):
    """Pass."""
    if value not in tools.EMPTY:

        value = tools.join_comma(value)
        if not this_data:
            msg = "Valid adapters:{valid}\n"
            msg = msg.format(
                valid=tools.join_cr(ctx.obj.adapters.get_known(adapters=prev_data))
            )
            ctx.echo_error(msg, abort=False)

            msg = "No adapters found when searching by {value_type}: {value}"
            msg = msg.format(value_type=value_type, value=value)
            ctx.echo_error(msg)

        msg = "Found {cnt} adapters by {value_type}: {value}"
        msg = msg.format(cnt=len(this_data), value_type=value_type, value=value)
        ctx.echo_ok(msg)


def kv_join(obj):
    """Pass."""
    kv_tmpl = "{}: {}".format
    items = [kv_tmpl(v["title"], v["value"]) for k, v in obj.items()]
    return join_cr(items)


def join_cr(obj):
    """Pass."""
    return tools.join_cr(obj=obj, pre=False, post=False, indent="")


def to_csv(ctx, raw_data, include_settings=True, **kwargs):
    """Pass."""
    rows = []

    simples = [
        "name",
        "node_name",
        "node_id",
        "status_raw",
        "cnx_count",
        "cnx_count_ok",
        "cnx_count_bad",
    ]

    cnx_tmpl = "cnx{idx}_{t}".format

    for adapter in raw_data:
        row = {k: adapter[k] for k in simples}

        for idx, cnx in enumerate(adapter["cnx"]):
            status = [
                "status: {}".format(cnx["status_raw"]),
                "error: {}".format(cnx["error"]),
            ]

            row[cnx_tmpl(idx=idx, t="id")] = cnx["id"]
            row[cnx_tmpl(idx=idx, t="status")] = join_cr(status)

            if include_settings:
                row[cnx_tmpl(idx=idx, t="settings")] = kv_join(cnx["config"])

        if include_settings:
            row["adapter_settings"] = kv_join(adapter["settings"])
            row["advanced_settings"] = kv_join(adapter["adv_settings"])

        rows.append(row)

    return context.dictwriter(rows=rows)


def to_json(ctx, raw_data, **kwargs):
    """Pass."""
    return tools.json_dump(obj=raw_data)
