# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import pathlib

import click
import OpenSSL

from ..context import CONTEXT_SETTINGS
from ..options import add_options

PEM_TYPE = OpenSSL.crypto.FILETYPE_PEM
ASN1_TYPE = OpenSSL.crypto.FILETYPE_ASN1

PATH = click.option(
    "--path",
    "-p",
    "path",
    type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=False),
    help="Path to SSL certificate to convert from binary to Base64",
    show_envvar=True,
    show_default=True,
    required=True,
)

OPTIONS = [PATH]


@click.command(name="convert-cert", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, path):
    """Convert an SSL Certificate from binary to Base64."""
    path = pathlib.Path(path).expanduser().resolve()
    contents = path.read_bytes()
    der = load_der(contents=contents)
    pem = der_to_pem(der=der)
    write_pem_path(ctx=ctx, path=path, pem=pem)
    ctx.exit(0)


def load_der(contents):
    """Load the bytes DER cert file into a python object."""
    return OpenSSL.crypto.load_certificate(ASN1_TYPE, contents)


def der_to_pem(der):
    """Convert a binary bytes DER cert to ascii PEM cert."""
    return OpenSSL.crypto.dump_certificate(PEM_TYPE, der)


def write_pem_path(ctx, path, pem):
    """Write an ascii PEM file to a path."""
    base_name = path.stem
    parent = path.parent
    pem_name = f"{base_name}.pem"
    pem_path = parent / pem_name
    if pem_path.is_file():
        ctx.obj.echo_error(f"Base64 SSL Certificate already exists: {pem_path}")
    pem_path.write_bytes(pem)
    ctx.obj.echo_ok(f"Wrote Base64 SSL Certificate to: {pem_path}")
    return pem_path
