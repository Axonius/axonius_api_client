# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import OPT_EXPORT_FORMAT, OPT_SECTION, str_section

OPTIONS = [*AUTH, OPT_EXPORT_FORMAT, OPT_SECTION]


@click.command(name="get-section", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, section, export_format):
    """Get settings for a section."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    apiname = ctx.parent.command.name.replace("-", "_")
    apiobj = getattr(client, apiname)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        settings = apiobj.get_section(section=section)

    if export_format == "str":
        str_section(meta=settings)
        ctx.exit(0)

    if export_format == "json-config":
        config = settings["config"]
        click.secho(json_dump(config))
        ctx.exit(0)

    if export_format == "json-full":
        click.secho(json_dump(settings))
        ctx.exit(0)

    ctx.exit(1)
