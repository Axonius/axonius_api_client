# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import echo_ok, json_dump, path_write
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import (
    OPT_ERROR_UNKNOWN,
    OPT_NAMES,
    OPT_SEP,
    OPTS_EXCLUDE,
    OPTS_EXPORT,
    OPTS_POSTFIX,
)


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
    *OPTS_EXPORT,
    *OPTS_POSTFIX,
    *OPTS_EXCLUDE,
    OPT_ERROR_UNKNOWN,
    OPT_SEP,
    OPT_NAMES,
]


@click.command(name="export", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_file, export_overwrite, **kwargs):
    """Export Dashboard Spaces."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.dashboard_spaces

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.export_spaces(**kwargs)
        echo_ok(f"Dashboard export info:\n{data}")
        handle_export(data=data, export_file=export_file, export_overwrite=export_overwrite)
