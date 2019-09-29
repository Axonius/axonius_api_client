# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, grp_cnx, options, serial


@click.command(name="get", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@options.OPT_INCLUDE_SETTINGS
@click.option(
    "--name",
    "-n",
    "names",
    help="Only include adapters with matching names.",
    multiple=True,
    show_envvar=True,
)
@click.option(
    "--name-regex",
    "-nax",
    "name_regex",
    help="Consider --name values as regular expressions.",
    is_flag=True,
    default=False,
    show_envvar=True,
)
@click.option(
    "--node",
    "-no",
    "nodes",
    help="Only include adapters with matching node names.",
    multiple=True,
    show_envvar=True,
)
@click.option(
    "--node-regex",
    "-nox",
    "node_regex",
    help="Consider --node values as regular expressions.",
    default=False,
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--min-count",
    "-min",
    "min_value",
    help="Only include adapters with at least this many connections.",
    type=click.INT,
    show_envvar=True,
)
@click.option(
    "--max-count",
    "-max",
    "max_value",
    help="Only include adapters with at most this many connections.",
    type=click.INT,
    show_envvar=True,
)
@click.option(
    "--no-cnx-working",
    "-ncw",
    "cnx_working",
    help="Exclude adapters with working connections.",
    is_flag=True,
    default=True,
    show_envvar=True,
)
@click.option(
    "--no-cnx-broken",
    "-ncb",
    "cnx_broken",
    help="Exclude adapters with broken connections.",
    is_flag=True,
    default=True,
    show_envvar=True,
)
@click.option(
    "--no-cnx-none",
    "-ncn",
    "cnx_none",
    help="Exclude adapters with no connections.",
    default=True,
    is_flag=True,
    show_envvar=True,
)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    export_format,
    export_file,
    export_path,
    export_overwrite,
    export_delim,
    names,
    name_regex,
    nodes,
    node_regex,
    min_value,
    max_value,
    cnx_working,
    cnx_broken,
    cnx_none,
    include_settings,
):
    """Get adapters based on name, node, or cnx status."""
    statuses = []

    if cnx_working:
        statuses.append(True)

    if cnx_broken:
        statuses.append(False)

    if cnx_none:
        statuses.append(None)

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        all_adapters = client.adapters.get()

        filter1 = client.adapters.filter_by_names(
            adapters=all_adapters, value=names, value_regex=name_regex
        )
        grp_cnx.grp_common.check_empty(
            ctx=ctx,
            this_data=filter1,
            prev_data=all_adapters,
            value_type="names",
            value=names,
            objtype="adapters",
            known_cb=client.adapters.get_known,
            known_cb_key="adapters",
        )

        filter2 = client.adapters.filter_by_nodes(
            adapters=filter1, value=nodes, value_regex=node_regex
        )
        grp_cnx.grp_common.check_empty(
            ctx=ctx,
            this_data=filter2,
            prev_data=filter1,
            value_type="node names",
            value=nodes,
            objtype="adapters",
            known_cb=client.adapters.get_known,
            known_cb_key="adapters",
        )

        filter3 = client.adapters.filter_by_cnx_count(
            adapters=filter2, min_value=min_value, max_value=max_value
        )
        grp_cnx.grp_common.check_empty(
            ctx=ctx,
            this_data=filter3,
            prev_data=filter2,
            value_type="connection counts",
            value="min_value {} and max_value {}".format(min_value, max_value),
            objtype="adapters",
            known_cb=client.adapters.get_known,
            known_cb_key="adapters",
        )

        filter4 = client.adapters.filter_by_status(adapters=filter3, value=statuses)
        grp_cnx.grp_common.check_empty(
            ctx=ctx,
            this_data=filter4,
            prev_data=filter3,
            value_type="statuses",
            value=statuses,
            objtype="adapters",
            known_cb=client.adapters.get_known,
            known_cb_key="adapters",
        )

    formatters = {"json": serial.to_json, "csv": to_csv}
    ctx.obj.handle_export(
        raw_data=filter4,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        joiner=export_delim,
        include_settings=include_settings,
    )


def to_csv(ctx, raw_data, include_settings=True, joiner="\n", **kwargs):
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
            row[cnx_tmpl(idx=idx, t="status")] = serial.join_cr(
                obj=status, joiner=joiner
            )

            if include_settings:
                row[cnx_tmpl(idx=idx, t="settings")] = serial.join_tv(
                    obj=cnx["config"], joiner=joiner
                )

        if include_settings:
            row["adapter_settings"] = serial.join_tv(
                obj=adapter["settings"], joiner=joiner
            )
            row["advanced_settings"] = serial.join_tv(
                obj=adapter["adv_settings"], joiner=joiner
            )

        rows.append(row)

    return serial.dictwriter(rows=rows)
