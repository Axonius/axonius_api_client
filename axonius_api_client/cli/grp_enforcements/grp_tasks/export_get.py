# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import codecs
import csv
import io

from ....api.json_api.tasks import Task
from ....tools import json_dump, path_write
from ...context import click


def export_csv(data, **kwargs):
    """Pass."""
    schemas = kwargs.get("schemas")
    explode = kwargs.get("explode")
    rows = list(
        Task.to_dicts(
            values=data,
            schemas=True if schemas is None else schemas,
            explode=True if explode is None else explode,
            as_csv=True,
        )
    )
    columns = list(rows[0].keys())
    stream = io.StringIO()

    try:
        stream.write(codecs.BOM_UTF8.decode("utf-8", "ignore"))
    except Exception:  # pragma: no cover
        pass

    writer = csv.DictWriter(
        stream,
        fieldnames=columns,
        quoting=csv.QUOTE_ALL,
        lineterminator="\n",
        dialect="excel",
        restval=None,
        extrasaction="raise",
    )
    for row in rows:
        writer.writerow(row)
    stream.seek(0)
    content = stream.getvalue()
    return content


def export_jsonl(data, **kwargs):
    """Pass."""
    schemas = kwargs.get("schemas")
    explode = kwargs.get("explode")
    rows = list(
        Task.to_dicts(
            values=data,
            schemas=False if schemas is None else schemas,
            explode=False if explode is None else explode,
        )
    )
    return "\n".join([json_dump(x, indent=None) for x in rows])


def export_json(data, **kwargs):
    """Pass."""
    schemas = kwargs.get("schemas")
    explode = kwargs.get("explode")
    rows = list(
        Task.to_dicts(
            values=data,
            schemas=False if schemas is None else schemas,
            explode=False if explode is None else explode,
        )
    )
    return json_dump(rows)


# noinspection PyUnusedLocal
def export_str(data, **kwargs):
    """Pass."""
    barrier = "-" * 80
    items = [f"{barrier}\n{x}" for x in data]
    return "\n\n".join(items)


EXPORT_FORMATS: dict = {
    "str": export_str,
    "json": export_json,
    "jsonl": export_jsonl,
    "csv": export_csv,
}
DEFAULT_EXPORT_FORMAT = list(EXPORT_FORMATS)[0]


def handle_export(
    ctx, data, export_format, export_file, export_overwrite, explode, schemas, **kwargs
):
    """Pass."""
    data_output = EXPORT_FORMATS[export_format](
        data=data, explode=explode, schemas=schemas, **kwargs
    )
    cnt_output = len(data_output.splitlines())
    cnt_tasks = len(data)
    cnt_results = sum([len(x.results) for x in data])
    counts = f"{cnt_tasks} tasks with {cnt_results} results and {cnt_output} lines"
    destination = export_file or "STDOUT"
    info = f"{counts} (export_format={export_format}, explode={explode}, schemas={schemas})"
    ctx.obj.echo_ok(f"Writing {info} to {destination!r}")
    if export_file:
        destination, _ = path_write(obj=export_file, data=data_output, overwrite=export_overwrite)
    else:
        click.secho(data_output)
    ctx.obj.echo_ok(f"Wrote {info} to {destination!r}")
