# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ... import cert_human
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import (
    OPT_PROMPT,
    OPT_UPDATE_ENV,
    confirm_cert,
    confirm_cert_replace,
    handle_update_env,
    split_leaf,
)

OPTIONS = [
    *AUTH,
    click.option(
        "--cert-file",
        "-cf",
        "cert_file_path",
        help="Path to custom SSL Certificate in PEM format.",
        metavar="PATH",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--key-file",
        "-kf",
        "key_file_path",
        help="Path to Key for --cert-file in PEM format",
        metavar="PATH",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--host",
        "-t",
        "host",
        required=True,
        show_envvar=True,
        show_default=True,
        help=(
            "Domain or IP of Axonius instance - must match one of the "
            "Subject Alternative Names defined in --cert-file."
        ),
    ),
    click.option(
        "--passphrase",
        "-p",
        "passphrase",
        help="Passphrase for --key-file (if protected with one).",
        metavar="PASSPHRASE",
        show_envvar=True,
        show_default=True,
        default="",
    ),
    OPT_PROMPT,
    OPT_UPDATE_ENV,
]


@click.command(name="gui-update", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    cert_file_path,
    key_file_path,
    host,
    passphrase,
    prompt,
    update_env,
):
    """Update GUI certificate from a PEM, PKCS7, or DER file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.settings_global

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        confirm_cert_replace(client=client, prompt=prompt)

        chain = cert_human.Cert.from_file(path=cert_file_path)
        leaf_cert, _ = split_leaf(chain=chain)

        input_file = leaf_cert.SOURCE["path"]
        _, valid_hosts = leaf_cert.is_valid_host(host=host)
        ctx.obj.echo_ok(f"Host {host!r} is valid for certificate, is one of: {valid_hosts}")

        confirm_cert(cert=leaf_cert, prompt=prompt)
        ctx.obj.echo_ok(f"Uploading new certificate from {input_file}")
        chain = apiobj.gui_cert_update_path(
            cert_file_path=cert_file_path,
            key_file_path=key_file_path,
            host=host,
            passphrase=passphrase,
        )
        ctx.obj.echo_ok(f"Successfully uploaded new certificate from {input_file}")
        split_leaf(chain=chain)
        handle_update_env(update_env=update_env, export_file=input_file)
    ctx.exit(0)
