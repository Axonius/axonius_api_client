# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ...tools import dt_now, path_write
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

now = dt_now().strftime("%Y-%m-%dT%H:%M:%S%z")

OPTIONS = [
    *AUTH,
    click.option(
        "--export-file",
        "-xf",
        "export_file",
        default="axonius_oas_{ax_version}_{ax_build_date}.yaml",
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


@click.command(name="get-spec", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_file, export_overwrite, **kwargs):
    """Get the OpenAPI specification file in YAML format."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.openapi.get_spec()

        if export_file:
            date = dt_now().strftime("%Y-%m-%dT%H:%M:%S%z")
            export_file = export_file.format(
                ax_version=client.version, ax_build_date=client.build_date, date=date
            )
            export_path, _ = path_write(obj=export_file, data=data, overwrite=export_overwrite)
            ctx.obj.echo_ok(f"OpenAPI YAML file exported to: {export_path}")
        else:
            click.secho(data)
    ctx.exit(0)
