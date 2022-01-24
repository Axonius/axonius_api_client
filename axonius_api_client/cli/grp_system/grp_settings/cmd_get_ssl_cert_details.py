# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options, SSL_CERT_EXPORT

OPTIONS = [*AUTH, SSL_CERT_EXPORT]


@click.command(name="get-ssl-cert-details", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get all settings."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    apiname = ctx.parent.command.name.replace("-", "_")
    apiobj = getattr(client, apiname)

    ssl_cert_information = apiobj.ssl_certificate_details()

    if export_format == "str":
        click.secho(f"issued_to: {ssl_cert_information.issued_to}")
        click.secho(f"alternative_names: {','.join(ssl_cert_information.alternative_names)}")
        click.secho(f"issued_by: {ssl_cert_information.issued_by}")
        click.secho(f"sha1_fingerprint: {ssl_cert_information.sha1_fingerprint}")
        click.secho(f"expires_on: {ssl_cert_information.expires_on}")
        ctx.exit(0)

    if export_format == "json":
        click.secho(json_dump(ssl_cert_information.to_dict()))
        ctx.exit(0)

    ctx.exit(1)
