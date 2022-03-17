# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import CONTEXT_SETTINGS
from ..options import add_options
from .grp_common import OPTS_EXPORT, from_path, handle_export

OPTIONS = [
    click.option(
        "--input-file",
        "-if",
        "input_file",
        help="Path to SSL certificate in DER or PKCS7 format to convert to PEM format",
        show_envvar=True,
        show_default=True,
        required=True,
    ),
    *OPTS_EXPORT,
]


@click.command(name="from-file", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, input_file, **kwargs):
    """Display/convert certificates from a PEM, DER, or PKCS7 file."""
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        chain = from_path(path=input_file, split=False)
        handle_export(data=chain, **kwargs)
    ctx.exit(0)
