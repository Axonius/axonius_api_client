# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....api.json_api.tasks.task_filters import build_include_options
from ...context import click
from ...options import AUTH, OPT_EXPORT_FILE, OPT_EXPORT_OVERWRITE
from .export_get_filters import EXPORT_FORMATS, DEFAULT_EXPORT_FORMAT

OPT_EXPORT_FORMAT = click.option(
    "--export-format",
    "-xt",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
    help="Format to write data as to STDOUT or --export-file.",
    default=DEFAULT_EXPORT_FORMAT,
    show_envvar=True,
    show_default=True,
)

OPTS_FILTERS = build_include_options()
OPTS_EXPORT = [OPT_EXPORT_FORMAT, OPT_EXPORT_FILE, OPT_EXPORT_OVERWRITE]

OPTIONS = [*AUTH, *OPTS_FILTERS, *OPTS_EXPORT]
