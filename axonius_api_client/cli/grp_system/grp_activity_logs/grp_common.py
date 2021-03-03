# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import csv
import io

from ....api.json_api.audit_logs import AuditLog
from ....tools import json_dump
from ...context import click

EXPORT = [
    click.option(
        "--export-format",
        "-xf",
        "export_format",
        type=click.Choice(["json-raw", "json", "str", "csv"]),
        help="Format to export data in",
        default="str",
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
        click.secho(json_dump([x.to_dict() for x in data]))
        ctx.exit(0)

    if export_format == "json-raw":
        click.secho(json_dump([x.raw for x in data]))
        ctx.exit(0)

    if export_format == "str":
        lines = [str(x) for x in data]
        click.secho("\n".join(lines))
        ctx.exit(0)

    if export_format == "csv":
        rows = [x.to_dict() for x in data]
        columns = AuditLog._search_properties()
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writerow(dict(zip(columns, columns)))
        writer.writerows(rows)
        content = stream.getvalue()
        stream.close()
        click.secho(content)

    ctx.exit(1)
