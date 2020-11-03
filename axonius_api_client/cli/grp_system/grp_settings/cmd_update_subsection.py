# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, SPLIT_CONFIG_OPT, add_options
from .grp_common import EXPORT, SECTION, SUB_SECTION, str_section

OPTIONS = [*AUTH, EXPORT, SECTION, SUB_SECTION, SPLIT_CONFIG_OPT]


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
    **kwargs,
):
    """Update a sub-section from arguments."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    new_config = dict(config)

    apiname = ctx.parent.command.name.replace("-", "_")
    apiobj = getattr(client, apiname)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        settings = apiobj.update_sub_section(section=section, sub_section=sub_section, **new_config)
        ctx.obj.echo_ok(f"Updated {sub_section!r} with configuration {new_config}")

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
