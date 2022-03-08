# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTIONS = [
    *AUTH,
    click.option(
        "--input-file",
        "-if",
        "input_file",
        help="Path to custom CA Certificate in PEM/DER/PKCS7 format.",
        metavar="PATH",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="ca-add", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file):
    """Add a CA Certificate from a file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.settings_global

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        path, data = apiobj.ca_add_path(path=input_file)
        ctx.obj.echo_ok(f"Added CA Certificate from {str(path)!r}")
        click.secho("\n".join(apiobj.cas_to_str(config=data)))
    ctx.exit(0)
