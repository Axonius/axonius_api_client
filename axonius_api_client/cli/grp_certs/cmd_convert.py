# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import CONTEXT_SETTINGS
from ..options import add_options
from .grp_common import der_to_pem, load_der

OPTIONS = [
    click.option(
        "--input-file",
        "-if",
        "input_file",
        help="Path to SSL certificate to convert from binary to Base64",
        type=click.File(mode="rb"),
        show_envvar=True,
        show_default=True,
        required=True,
    ),
    # XXX input-file-format (AUTO, PEM, DER, PKCS, ETC)
    # XXX output-file-format
    click.option(
        "--output-file",
        "-of",
        "output_file",
        help="Path to write converted file to (default: '{cert-path}.pem')",
        show_envvar=True,
        show_default=True,
        required=False,
    ),
    click.option(
        "--output-overwrite/--no-output-overwrite",
        "-xo/-nxo",
        "output_overwrite",
        default=False,
        help="If --output-file exists, overwrite it",
        is_flag=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="convert", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, input_file, output_file, output_overwrite):
    """Convert an SSL Certificate from binary to Base64."""
    contents = ctx.obj.read_stream(stream=input_file)
    ctx.obj.echo_debug(f"Read {len(contents)} bytes from {input_file}")

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        der = load_der(value=contents)
        import pdb

        pdb.set_trace()
        ctx.obj.echo_debug(f"Loaded certificate as X509 object: {der}")

        pem = der_to_pem(der=der)
        ctx.obj.echo_debug(f"Converted X509 object to PEM: {pem}")

        # base_name = path.stem
        # parent = path.parent
        # pem_name = f"{base_name}.pem"
        # pem_path = parent / pem_name
        # if pem_path.is_file():
        #     ctx.obj.echo_error(f"Base64 SSL Certificate already exists: {pem_path}")
        # pem_path.write_bytes(pem)

        # ctx.obj.echo_ok(f"Wrote Base64 SSL Certificate to: {pem_path}")

    ctx.exit(0)
