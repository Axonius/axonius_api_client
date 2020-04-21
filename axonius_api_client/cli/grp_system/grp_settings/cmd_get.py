# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json-full", "json-config", "str"]),
    help="Format of to export data in",
    default="json-config",
    show_envvar=True,
    show_default=True,
)

OPTIONS = [*AUTH, EXPORT]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get all settings."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    settings_name = ctx.parent.command.name.replace("-", "_")
    settings_obj = getattr(client.system, settings_name)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = settings_obj.get()

    if export_format == "str":
        config_sections(ctx=ctx, data=data)
    if export_format == "json-config":
        click.secho(json_dump(data["config"]))
        ctx.exit(0)

    if export_format == "json-full":
        click.secho(json_dump(data))
        ctx.exit(0)

    ctx.exit(1)


def config_sections(ctx, data):
    """Pass."""
    settings_title = data["title"]
    settings_config = data["config"]
    click.secho(f"Settings: {settings_title}")

    for section, meta in data["sections"].items():
        title = data["section_titles"][section]
        config = settings_config[section]
        click.secho(f"\nSection {title}:\n  {section}")
        config_section(ctx=ctx, parent_meta=meta, section_config=config)


def config_section(ctx, parent_meta, section_config):
    """Pass."""
    for section, meta in parent_meta.items():
        config = section_config[section]
        title = meta.get("title", "")
        ikey = "    *  "
        ival = "       "
        if meta.get("sub_schemas"):
            # config_sub_section(ctx, parent_meta, section_config)
            pass
        else:
            click.secho(f"{ikey}{title}\n{ival}{section}: {config}")


# def config_sub_section(ctx, parent_meta, section_config):
#     """Pass."""
#     for item_name, item_meta in meta.get("sub_schemas"):
#         item_config = config[item_name]
#         click.secho(f"    * {sub_section_title}: {sub_section_config!r}")
