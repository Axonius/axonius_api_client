# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import json

from ....tools import listify
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from ....tools import dt_now, path_write


OPTIONS = [
    *AUTH,
    click.option(
        "--uuid",
        "-u",
        "uuids",
        help="UUIDs of saved queries (multiple)",
        multiple=True,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--name",
        "-n",
        "names",
        help="Names of saved queries (multiple)",
        multiple=True,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
      "--folder-id",
        "-f",
        "folder_id",
        default="",
        help="Folder ID to export from",
        multiple=False,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--export-file",
        "-xf",
        "export_file",
        default="axonius_saved_queries_{timestamp}UTC.json",
        help="File to send data to",
        show_envvar=True,
        show_default=True,
        metavar="PATH",
        required=False,
    ),
    click.option(
        "--export-overwrite/--no-export-overwrite",
        "-xo/-nxo",
        "export_overwrite",
        default=False,
        help="If --export-file supplied and it exists, overwrite it",
        is_flag=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="export", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, uuids, names, folder_id, export_file, export_overwrite):
    """Export saved queries to a file."""

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        uuids = listify(uuids)
        names = listify(names)
        for name in names:
            uuid = apiobj.saved_query.get_by_name(value=name, as_dataclass=True).uuid
            uuids.append(uuid)
        ctx.obj.echo_ok(f"Exporting saved queries: uuids={uuids}")
        data = apiobj.saved_query.saved_query_export(ids=uuids, folder_id=folder_id, as_dataclass=True)
        if export_file:
            date = dt_now().strftime("%Y-%m-%dT%H-%M-%S")
            export_file = export_file.format(timestamp=date)
            export_path, _ = path_write(obj=export_file, data=json.dumps(data, indent=4), overwrite=export_overwrite)
            ctx.obj.echo_ok(f"Saved queries exported to: {export_path}")
        else:
            click.secho(data)
    ctx.exit(0)
