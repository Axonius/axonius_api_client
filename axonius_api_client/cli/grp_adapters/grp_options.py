# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import click
from ..options import AUTH, CONTENTS, NODE, SPLIT_CONFIG_REQ

GET = [
    *AUTH,
    click.option(
        "--export-format",
        "-xf",
        "export_format",
        type=click.Choice(["json-full", "json", "table", "str", "str-args"]),
        help="Format of to export data in",
        default="str",
        show_envvar=True,
        show_default=True,
    ),
]


CONFIG_EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json-full", "json"]),
    help="Format of to export data in",
    default="json",
    show_envvar=True,
    show_default=True,
)

CONFIG_TYPE = click.option(
    "--generic/--specific",
    "-g/-s",
    "generic",
    default=True,
    show_envvar=True,
    show_default=True,
    help="Generic or adapter specific config",
)

CONFIG_GET = [
    *AUTH,
    CONFIG_EXPORT,
    CONFIG_TYPE,
    *NODE,
]

CONFIG_UPDATE = [*CONFIG_GET, SPLIT_CONFIG_REQ]
CONFIG_UPDATE_FILE = [*CONFIG_GET, CONTENTS]
FILE_UPLOAD = [
    *AUTH,
    *NODE,
    # field_name
    # file_name
    CONTENTS,
]
