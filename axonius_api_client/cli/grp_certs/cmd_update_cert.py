# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTIONS = [
    *AUTH,
    click.option(
        "--enabled/--disabled",
        "-e/-d",
        "enabled",
        default=True,
        help="Enable the use of the custom SSL certificate.",
        show_envvar=True,
        show_default=True,
        is_flag=True,
        hidden=False,
    ),
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
        help="Path to SSL Key file for --cert-file in PEM format",
        metavar="PATH",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--hostname",
        "-hn",
        "hostname",
        required=True,
        show_envvar=True,
        show_default=True,
        help="Hostname of Axonius instance - must match the value of the Common Name (CN) attribute from --cert-file.",  # noqa: E501
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
]


@click.command(name="update", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    cert_file_path,
    key_file_path,
    hostname,
    enabled,
    passphrase,
):
    """Update the SSL certificate."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiname = ctx.parent.command.name.replace("-", "_")
    apiobj = getattr(client, apiname)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.ssl_update_path(
            cert_file_path=cert_file_path,
            key_file_path=key_file_path,
            hostname=hostname,
            enabled=enabled,
            passphrase=passphrase,
        )

    click.secho(f"{data}")
    ctx.exit(0)
