# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import OPTS_CSR, OPTS_CSR_EXPORT, handle_export

OPTIONS = [
    *AUTH,
    *OPTS_CSR_EXPORT,
    *OPTS_CSR,
]


@click.command(name="csr-create", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Create a Certificate Signing Request."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.settings_global

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.csr_create(**kwargs)
        ctx.obj.echo_ok(f"Created CSR: {data}")
        handle_export(data=data, **kwargs)
