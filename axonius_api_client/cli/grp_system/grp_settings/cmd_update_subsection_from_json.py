# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, INPUT_FILE, add_options
from .grp_common import OPT_EXPORT_FORMAT, OPT_SECTION, OPT_SUB_SECTION, str_section

OPTIONS = [*AUTH, OPT_EXPORT_FORMAT, OPT_SECTION, OPT_SUB_SECTION, INPUT_FILE]


@click.command(name="update-sub-section-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    input_file,
    section,
    sub_section,
    export_format,
    **kwargs,
):
    """Update a subsection from a JSON file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    new_config = ctx.obj.read_stream_json(stream=input_file, expect=dict)

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
