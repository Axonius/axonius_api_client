# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import URL, add_options
from .grp_common import (
    OPT_EXPORT_FILE_PEM,
    OPT_PROMPT,
    OPT_UPDATE_ENV,
    confirm_cert,
    from_path,
    from_url,
    handle_export,
    handle_update_env,
    pathify_export_file,
    split_leaf,
)

OPTIONS = [
    URL,
    click.option(
        "--include-url",
        "-iu",
        "include_urls",
        help="Include certificates fetched from URLs",
        show_envvar=True,
        show_default=True,
        required=False,
        multiple=True,
    ),
    click.option(
        "--include-path",
        "-ip",
        "include_paths",
        help="Include certificates from files in DER, PEM, or PKCS7 format",
        show_envvar=True,
        show_default=True,
        required=False,
        multiple=True,
    ),
    click.option(
        "--include-only-ca/--no-include-only-ca",
        "-ioc/-nioc",
        "include_only_ca",
        default=True,
        help="Only include certificates marked as CA's from --include-path or --include-url",
        is_flag=True,
        show_envvar=True,
        show_default=True,
    ),
    OPT_EXPORT_FILE_PEM,
    OPT_PROMPT,
    OPT_UPDATE_ENV,
]


@click.command(name="gui-get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    prompt,
    include_paths,
    include_urls,
    include_only_ca,
    export_file,
    update_env,
):
    """Get GUI certificate and export to a PEM file."""
    client = ctx.obj.create_client(url=url, key=None, secret=None)
    export_file = pathify_export_file(client=client, export_file=export_file)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        includes = []

        for url in include_urls:
            includes += from_url(url=url, split=False, ca_only=include_only_ca)

        for path in include_paths:
            includes += from_path(path=path, split=False, ca_only=include_only_ca)

        chain = client.HTTP.get_cert_chain()
        leaf_cert, intm_certs = split_leaf(chain=chain)
        prompt = confirm_cert(prompt=prompt, cert=leaf_cert)
        handle_export(
            data=chain + includes,
            export_file=export_file,
            export_backup=True,
            export_format="pem",
        )
        handle_update_env(update_env=update_env, export_file=export_file)

    ctx.exit(0)
