# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import echo_ok, json_dump, path_write
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, INPUT_FILE, add_options
from .grp_common import OPT_REPLACE, OPTS_EXCLUDE, OPTS_POSTFIX


def handle_export(data, export_file, export_overwrite=False):
    """Pass."""
    data_dict = data.to_dict()
    output = json_dump(data_dict)
    if export_file:
        export_path, data = path_write(obj=export_file, data=output, overwrite=export_overwrite)
        byte_len, backup_path = data
        echo_ok(f"Wrote dashboard spaces export to: '{export_path}' ({byte_len} bytes)")
    else:
        click.secho(output)
        echo_ok("Wrote dashboard spaces export to STDOUT")


OPTIONS = [
    *AUTH,
    *OPTS_POSTFIX,
    *OPTS_EXCLUDE,
    OPT_REPLACE,
    INPUT_FILE,
]


@click.command(name="import", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file, **kwargs):
    """Import Dashboard Spaces."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.dashboard_spaces
    kwargs["data"] = ctx.obj.read_stream_json(stream=input_file, expect=dict)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data_obj = apiobj.load_export_data(**kwargs)
        echo_ok(f"Dashboard Spaces export loaded:\n{data_obj}")
        data = apiobj.import_spaces(**kwargs)
        echo_ok(f"Import completed:\n{data}")
