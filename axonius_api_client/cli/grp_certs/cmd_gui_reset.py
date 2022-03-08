# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import (
    OPT_EXPORT_FILE_PEM,
    OPT_PROMPT,
    OPT_UPDATE_ENV,
    confirm_cert_replace,
    handle_export,
    handle_update_env,
    pathify_export_file,
    split_leaf,
)

OPTIONS = [
    *AUTH,
    OPT_EXPORT_FILE_PEM,
    OPT_PROMPT,
    OPT_UPDATE_ENV,
]


@click.command(name="gui-reset", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    prompt,
    export_file,
    update_env,
):
    """Reset GUI certificate to default."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.settings_global
    export_file = pathify_export_file(client=client, export_file=export_file)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        confirm_cert_replace(client=client, prompt=prompt)
        chain = apiobj.gui_cert_reset(verified=True)
        leaf_cert, intm_certs = split_leaf(chain=chain)

        ctx.obj.echo_ok(f"SSL certificate reset to default: {leaf_cert}")
        handle_export(
            data=chain,
            export_file=export_file,
            export_backup=True,
            export_format="pem",
        )
        handle_update_env(update_env=update_env, export_file=export_file)

    ctx.exit(0)
