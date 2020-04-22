# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import click

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json-full", "json-config", "str"]),
    help="Format of to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)

SECTION = click.option(
    "--section",
    "-se",
    "section",
    help="Settings section internal name (not title)",
    required=True,
    show_envvar=True,
    show_default=True,
)

SUB_SECTION = click.option(
    "--sub-section",
    "-sb",
    "sub_section",
    help="Settings sub section internal name (not title)",
    required=True,
    show_envvar=True,
    show_default=True,
)


def config_sections(ctx, settings):
    """Pass."""
    settings_title = settings["title"]
    settings_config = settings["config"]
    click.secho(f"Settings: {settings_title}")

    for section, meta in settings["sections"].items():
        title = settings["section_titles"][section]
        config = settings_config[section]
        click.secho(f"\n{section:25}  ## SECTION {title}:")
        config_section(ctx=ctx, parent_meta=meta, section_config=config)


def config_section(ctx, parent_meta, section_config):
    """Pass."""
    for section, meta in parent_meta.items():
        config = section_config[section]

        if meta.get("sub_schemas"):
            title = meta.get("title", "")
            click.secho(f"\n    {section:30}  ## SUB SECTION {title}")

            config_sub_section(ctx=ctx, parent_meta=meta, section_config=config)
        else:
            title = meta["title"]
            ctype = meta["type"]
            value = f"{section}={config!r}"
            click.secho(f"   {value:30}  ## {title} ({ctype!r})")


def config_sub_section(ctx, parent_meta, section_config):
    """Pass."""
    for section, meta in parent_meta.get("sub_schemas").items():
        config = section_config[section]
        title = meta["title"]
        ctype = meta["type"]
        value = f"{section}={config!r}"
        click.secho(f"        {value:30}  ## {title} ({ctype!r})")


def handle_export(ctx, settings, export_format, section=None, **kwargs):
    """Pass."""
    if export_format == "str":
        config_sections(ctx=ctx, settings=settings)
        ctx.exit(0)

    if export_format == "json-config":
        if section:
            config = settings["config"][section]
        else:
            config = settings["config"]

        click.secho(json_dump(config))
        ctx.exit(0)

    if export_format == "json-full":
        click.secho(json_dump(settings))
        ctx.exit(0)

    ctx.exit(1)
