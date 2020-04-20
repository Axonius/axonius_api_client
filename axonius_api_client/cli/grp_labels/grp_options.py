# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import click
from ..options import AUTH

LABELS_GET = AUTH
LABELS_ACT = [
    *AUTH,
    click.option(
        "--label",
        "-l",
        "labels",
        help="Labels to process",
        required=True,
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--rows",
        "-r",
        "rows",
        help="The rows in JSON format to process as a file or via stdin",
        default="-",
        type=click.File(mode="r"),
        show_envvar=True,
        show_default=True,
    ),
]
