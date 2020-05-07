# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import click

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json-full", "json", "str"]),
    help="Format of to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)


def echo_key(data, key):
    """Pass."""
    value = data[key]

    key = key.replace("_", " ").title()

    if isinstance(value, list):
        value = ", ".join(value)

    click.secho(f"{key}: {value}")


def echo_fetch_progress(data, key):
    """Pass."""
    phases = data["phases"]
    fetch = [x for x in phases if x["name"] == key][0]
    key = key.replace("_", " ").title()

    progress = fetch["progress"]
    for status, adapters in progress.items():
        adapters = ", ".join(adapters)
        click.secho(f"Phase {key} {status}: {adapters}\n")


def handle_export(ctx, data, export_format, **kwargs):
    """Pass."""
    if export_format == "json":
        data.pop("phases")
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "json-full":
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "str":
        echo_fetch_progress(data, "Fetch_Devices")
        echo_fetch_progress(data, "Fetch_Scanners")
        keys = [
            "last_start_date",
            "last_finish_date",
            "last_took_minutes",
            "next_start_date",
            "next_in_minutes",
            "is_running",
            "phases_done",
            "phases_pending",
        ]
        for key in keys:
            echo_key(data, key)

        ctx.exit(0)

    ctx.exit(1)
