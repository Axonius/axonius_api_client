# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, options, serial
from . import grp_common


@click.command(name="delete", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@options.OPT_INCLUDE_SETTINGS
@options.OPT_NO_ERROR
@options.OPT_WAIT_DELETE
@click.option(
    "--delete-entities",
    "-de",
    "delete_entities",
    help="Delete information for this connection from associated assets.",
    default=False,
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--force",
    "-f",
    "force",
    help="Actually delete the connections.",
    default=False,
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--show-sources",
    "-ss",
    help="Print the source commands that can be supplied as valid input to -r/--rows.",
    default=False,
    is_flag=True,
    is_eager=True,
    callback=grp_common.show_sources,
    expose_value=False,
)
@options.OPT_ROWS
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
    rows,
    delete_entities,
    wait,
    error,
    force,
    include_settings,
):
    """Delete an adapter connection."""
    rows = grp_common.get_rows(ctx=ctx, rows=rows, only_parent=False)

    processed = []

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    found_error = False

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        for cnx in rows:
            info_keys = ["adapter_name", "node_name", "id", "uuid", "status", "error"]
            cnxinfo = {k: cnx[k] for k in info_keys}

            msg = "In {s} second will delete connection: {ci}"
            msg = msg.format(s=wait, ci=serial.join_kv(obj=cnxinfo, indent=" " * 4))
            ctx.obj.echo_warn(msg)

            raw_data = client.adapters.cnx.delete(
                cnx=cnx,
                delete_entities=delete_entities,
                force=force,
                error=False,
                sleep=wait,
                warning=False,
            )

            processed.append(raw_data)

            action = "deleting"
            had_error, had_cnx_error = grp_common.handle_response(
                ctx=ctx, cnx=raw_data, action=action, cnx_error=False
            )

            if had_error:
                found_error = True
                if error:
                    break

    formatters = {"json": serial.to_json, "csv": grp_common.to_csv}

    ctx.obj.handle_export(
        raw_data=processed,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        joiner=export_delim,
        include_settings=include_settings,
    )

    ctx.exit(int(found_error))
