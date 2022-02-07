# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import time
from typing import Optional

from ....tools import json_dump
from ...context import click


class Defaults:
    """Pass."""

    export_format: str = "str"
    sleep: int = 60
    for_next_minutes: Optional[int] = None
    wait: bool = False
    phases: bool = True
    progress: bool = False


def export_str(
    data,
    phases=Defaults.phases,
    progress=Defaults.progress,
    **kwargs,
):
    """Pass."""

    def join(obj):
        return "\n - " + "\n - ".join(obj)

    props = data.to_str_properties()

    lines = [f"Properties:{join(props)}"]
    if phases:
        phases = data.to_str_phases()
        lines += ["", f"Phase Status:{join(phases)}"]
    if progress:  # pragma: no cover
        progress = data.to_str_progress() or ["n/a"]
        lines += ["", f"Phase Progress:{join(progress)}"]
    return "\n".join(lines)


def export_json(data, **kwargs):
    """Pass."""
    return json_dump(data.to_dict())


def export_json_raw(data, **kwargs):
    """Pass."""
    return json_dump(data.raw)


EXPORT_FORMATS: dict = {
    "json-raw": export_json_raw,
    "json": export_json,
    "str": export_str,
}


OPTS_EXPORT = [
    click.option(
        "--export-format",
        "-xf",
        "export_format",
        type=click.Choice(list(EXPORT_FORMATS)),
        help="Format of to export data in",
        default=Defaults.export_format,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--include-phases/--no-include-phases",
        "-iph/-niph",
        "phases",
        help="Include status of phases in string output",
        is_flag=True,
        default=Defaults.phases,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--include-progress/--no-include-progress",
        "-ipr/-nipr",
        "progress",
        help="Include progress of phases in string output",
        is_flag=True,
        default=Defaults.progress,
        show_envvar=True,
        show_default=True,
    ),
]

OPT_SLEEP = click.option(
    "--sleep",
    "sleep",
    help="Seconds to wait for each stability check",
    type=click.INT,
    default=Defaults.sleep,
    show_envvar=True,
    show_default=True,
)


def wait_stable(
    client,
    ctx,
    export_format: str = Defaults.export_format,
    for_next_minutes: Optional[int] = Defaults.for_next_minutes,
    sleep: int = Defaults.sleep,
    wait: bool = Defaults.wait,
    phases: bool = Defaults.phases,
    progress: bool = Defaults.progress,
):
    """Pass."""
    is_stable = False
    data = client.dashboard.get()
    reason, is_stable = data.get_stability(for_next_minutes=for_next_minutes)

    while wait and not is_stable:  # pragma: no cover
        ctx.obj.echo_warn(
            f"Data is stable: {is_stable}, reason: {reason}, sleeping {sleep} seconds"
        )
        time.sleep(sleep)
        data = client.dashboard.get()
        click.secho(EXPORT_FORMATS[export_format](data=data, phases=phases, progress=progress))
        reason, is_stable = data.get_stability(for_next_minutes=for_next_minutes)

    click.secho(EXPORT_FORMATS[export_format](data=data, phases=phases, progress=progress))
    ctx.obj.echo_ok(f"Data is stable: {is_stable}, reason: {reason}")

    return data
