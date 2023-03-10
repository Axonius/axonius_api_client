# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from .grp_common import AX_ENV, EXPORT_FORMATS

OPT_EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
    help="Format of to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)

OPT_ENV = click.option(
    "--env",
    "-e",
    "env",
    default=AX_ENV,
    help="Path to .env file when --export-format==env",
    show_envvar=True,
    show_default=True,
)
