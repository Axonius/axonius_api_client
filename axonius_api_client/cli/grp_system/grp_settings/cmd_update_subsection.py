# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, SPLIT_CONFIG_OPT, add_options
from .grp_common import OPT_EXPORT_FORMAT, OPT_SECTION, OPT_SUB_SECTION, str_section

OPTIONS = [*AUTH, OPT_EXPORT_FORMAT, OPT_SECTION, OPT_SUB_SECTION, SPLIT_CONFIG_OPT]


@click.command(name="update-sub-section", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    config,
    section,
    sub_section,
    export_format,
):
    """Update a subsection from arguments."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    config = dict(config)

    apiname = ctx.parent.command.name.replace("-", "_")
    apiobj = getattr(client, apiname)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        settings = apiobj.update_sub_section(section=section, sub_section=sub_section, **config)
        ctx.obj.echo_ok(f"Updated {sub_section!r} with configuration {config}")

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
