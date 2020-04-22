# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT, SECTION, config_sections

OPTIONS = [*AUTH, EXPORT, SECTION]


@click.command(name="get-sub-section", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, section, export_format, **kwargs):
    """Get settings for a specific section."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    settings_name = ctx.parent.command.name.replace("-", "_")
    settings_obj = getattr(client.system, settings_name)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        settings = settings_obj.get()
        settings_obj.get_section(section=section, settings=settings, config=False)
        settings["sections"] = {
            k: v for k, v in settings["sections"].items() if k == section
        }
        settings["config"] = {
            k: v for k, v in settings["config"].items() if k == section
        }

    if export_format == "str":
        config_sections(ctx=ctx, settings=settings)
        ctx.exit(0)

    if export_format == "json-config":
        click.secho(json_dump(settings["config"][section]))
        ctx.exit(0)

    if export_format == "json-full":
        click.secho(json_dump(settings))
        ctx.exit(0)

    ctx.exit(1)
