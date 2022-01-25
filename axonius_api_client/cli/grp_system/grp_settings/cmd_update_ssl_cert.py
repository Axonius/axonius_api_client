# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, SPLIT_CONFIG_OPT, add_options, SSL_UPDATE
from .grp_common import EXPORT, SECTION, str_section


OPTIONS = [*AUTH, *SSL_UPDATE]


@click.command(name="update-ssl-cert", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    cert_file,
    key_file,
    hostname,
    enabled,
    passphrase,
    **kwargs,
):
    """Update the SSL certificate."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    apiname = ctx.parent.command.name.replace("-", "_")
    apiobj = getattr(client, apiname)

    cert_file_path = format(getattr(cert_file, "name", cert_file))
    key_file_path = format(getattr(key_file, "name", key_file))

    response = apiobj.ssl_update_path(
        cert_file_path=cert_file_path,
        key_file_path=key_file_path,
        hostname=hostname,
        enabled=enabled,
        passphrase=passphrase,
    )

    if response:
        click.secho(str(response))

    ctx.exit(1)
