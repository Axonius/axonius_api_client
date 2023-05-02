# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....api.json_api.tasks.task_filters import TaskFilters, ATTR_MAP
from ....tools import json_dump, path_write
from ...context import click


def export_json(data, **kwargs) -> str:
    """Pass."""
    data_dict = data.to_dict()
    for k, v in ATTR_MAP.items():
        if not kwargs.get(k, True):
            data_dict.pop(v["TaskFilters"], None)
    return json_dump(data_dict)


def export_str(data: TaskFilters, **kwargs):
    """Pass."""
    barrier = "-" * 80
    items = []

    for k, v in ATTR_MAP.items():
        if kwargs.get(k, True):
            value = getattr(data, v["enum"])
            if k == "task_ids":
                value = [f"Min: {min(value)}", f"Max: {max(value)}"]
            else:
                value = [str(x) for x in getattr(data, v["enum"])]
            items += [barrier, v["desc"], *value, ""]
    return "\n".join(items)


EXPORT_FORMATS: dict = {
    "str": export_str,
    "json": export_json,
}
DEFAULT_EXPORT_FORMAT = list(EXPORT_FORMATS)[0]


def handle_export(ctx, export_format, export_file, export_overwrite, data, **kwargs):
    """Pass."""
    data_output = EXPORT_FORMATS[export_format](data=data, **kwargs)
    cnt_output = len(data_output.splitlines())
    counts = f"with {cnt_output} lines"
    destination = export_file or "STDOUT"
    info = f"TaskFilters {counts} (export_format={export_format})"

    ctx.obj.echo_ok(f"Writing {info} to {destination!r}")
    if export_file:
        path, _ = path_write(obj=export_file, data=data_output, overwrite=export_overwrite)
    else:
        click.secho(data_output)
    ctx.obj.echo_ok(f"Wrote {info} to {destination!r}")
