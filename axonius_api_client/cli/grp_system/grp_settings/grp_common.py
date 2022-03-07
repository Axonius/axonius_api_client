# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
# from ....tools import json_dump
from ...context import click

OPT_EXPORT_FORMAT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json-full", "json-config", "str"]),
    help="Format of to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)

OPT_SECTION = click.option(
    "--section",
    "-se",
    "section",
    help="Settings section internal name (not title)",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_SUB_SECTION = click.option(
    "--sub-section",
    "-sb",
    "sub_section",
    help="Settings sub section internal name (not title)",
    required=True,
    show_envvar=True,
    show_default=True,
)


def str_sections(meta):
    """Pass."""
    settings_title = meta["settings_title"]
    click.secho(f"Settings: {settings_title}")

    sections = meta["sections"]

    for name, meta in sections.items():
        str_section(meta=meta)


def str_section(meta):
    """Pass."""
    name = meta["name"]
    title = meta["title"]
    settings_title = meta["settings_title"]

    lines = [
        f"Section Name: {name!r}",
        f"Section Title: {settings_title}: {title}",
    ]
    join = "\n- "
    click.secho(join + join.join(lines))
    str_schemas(schemas=meta["schemas"], config=meta["config"], indent=4)

    sub_sections = meta["sub_sections"]
    for sub_name, sub_meta in sub_sections.items():
        str_subsection(meta=sub_meta)


def str_subsection(meta):
    """Pass."""
    name = meta["name"]
    title = meta["title"]
    settings_title = meta["settings_title"]
    parent_title = meta["parent_title"]

    lines = [
        f"Sub Section Name: {name!r}",
        f"Sub Section Title: {settings_title}: {parent_title}: {title}",
    ]
    join = "\n--- "
    click.secho(join + join.join(lines))
    str_schemas(schemas=meta["schemas"], config=meta["config"], indent=6)


def str_schemas(schemas, config, indent=4):
    """Pass."""
    join = "\n{}".format(" " * indent)
    for name, schema in schemas.items():
        title = schema.get("title")
        stype = schema["type"]
        value = config[name]

        lines = [
            f"Name: {name}",
            f"Title: {title}",
            f"Type: {stype!r}",
            f"Value: {name}={value!r}",
        ]
        click.secho(join + join.join(lines))
