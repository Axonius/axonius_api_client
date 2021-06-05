# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import time

from ....tools import json_dump
from ...context import click

EXPORT = [
    click.option(
        "--export-format",
        "-xf",
        "export_format",
        type=click.Choice(["json-raw", "json", "str"]),
        help="Format of to export data in",
        default="str",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--include-phases/--no-include-phases",
        "-iph/-niph",
        "include_phases",
        help="Include status of phases in string output",
        is_flag=True,
        default=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--include-progress/--no-include-progress",
        "-ipr/-nipr",
        "include_progress",
        help="Include progress of phases in string output",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
]


def join(obj):
    """Pass."""
    return "\n - " + "\n - ".join(obj)


def handle_export(ctx, data, export_format, **kwargs):
    """Pass."""
    if export_format == "json":
        click.secho(json_dump(data.to_dict()))
        ctx.exit(0)

    if export_format == "json-raw":
        click.secho(json_dump(data.raw))
        ctx.exit(0)

    if export_format == "str":
        lines = []

        props = data.to_str_properties()
        lines += [f"Properties:{join(props)}"]

        if kwargs.get("include_phases"):
            phases = data.to_str_phases()
            lines += ["", f"Phase Status:{join(phases)}"]

        if kwargs.get("include_progress"):
            progress = data.to_str_progress() or ["n/a"]
            lines += ["", f"Phase Progress:{join(progress)}"]

        click.secho("\n".join(lines))

        ctx.exit(0)

    ctx.exit(1)


def get_stability(data, for_next_minutes=None):
    """Pass."""
    if data.is_running:
        if data.is_correlation_finished:
            return "Discover is running but correlation has finished", True

        return "Discover is running and correlation has NOT finished", False

    next_mins = data.next_run_starts_in_minutes
    reason = f"Discover is not running and next is in {next_mins} minutes"

    if for_next_minutes:
        if data.next_run_within_minutes(for_next_minutes):
            return f"{reason} (less than {for_next_minutes} minutes)", False
        return f"{reason} (more than {for_next_minutes} minutes)", True

    return reason, True


def do_wait_discover(ctx, client, sleep=60, for_next_minutes=None, **kwargs):
    """Pass."""
    while True:
        with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
            data = client.dashboard.get()

        reason, is_stable = get_stability(data=data, for_next_minutes=for_next_minutes)

        if is_stable:
            click.secho(f"Data is stable: {is_stable}, reason: {reason}")
            return reason, is_stable

        click.secho(f"Data is stable: {is_stable}, reason: {reason}, sleeping {sleep} seconds")
        time.sleep(sleep)
