# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

ENABLED = click.option(
    "--enable/--no-enable",
    "enabled",
    default=None,
    help="Enable or disable 'Global Settings > API Settings'",
    is_flag=True,
    multiple=False,
    required=True,
    show_default=True,
    show_envvar=True,
)
DESTROY = click.option(
    "--destroy/--no-destroy",
    "destroy",
    default=None,
    help="Enable or disable 'Global Settings > API Settings > Enable API destroy endpoints'",
    is_flag=True,
    multiple=False,
    required=True,
    show_default=True,
    show_envvar=True,
)
RESET = click.option(
    "--reset/--no-reset",
    "reset",
    default=None,
    help="Enable or disable 'Global Settings > API Settings > Enable factory reset endpoints'",
    is_flag=True,
    multiple=False,
    required=True,
    show_default=True,
    show_envvar=True,
)


OPTIONS = [*AUTH, ENABLED, DESTROY, RESET]


@click.command(name="configure-destroy", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, enabled, reset, destroy):
    """Enable or disable dangerous API endpoints."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.settings_global.configure_destroy(
            enabled=enabled, reset=reset, destroy=destroy
        )

    settings_title = data["settings_title"]
    section_title = data["title"]
    schemas = data["schemas"]
    config = data["config"]

    for key, schema in schemas.items():
        schema_title = schema["title"]
        config_value = config.get(key)
        click.secho(f"{settings_title} > {section_title} > {schema_title}: {config_value}")
    ctx.exit(0)
