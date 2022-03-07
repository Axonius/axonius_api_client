# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTIONS = [
    *AUTH,
    click.option(
        "--filename",
        "-fn",
        "filenames",
        help="Name of CA certificate to remove. (multiples)",
        multiple=True,
        required=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="ca-remove", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, filenames):
    """Remove a CA Certificate by filename."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.settings_global

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        for filename in filenames:
            data = apiobj.ca_remove(filename=filename)
            ctx.obj.echo_ok(f"Removed CA certificate {filename!r}")

        click.secho("\n".join(apiobj.cas_to_str(config=data)))

    ctx.exit(0)
