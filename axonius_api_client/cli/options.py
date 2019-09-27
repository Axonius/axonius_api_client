# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import click

from .. import tools

OPT_URL = click.option(
    "--url",
    "-u",
    "url",
    required=True,
    help="URL of Axonius instance.",
    metavar="URL",
    prompt="URL of Axonius instance",
    show_envvar=True,
)
OPT_KEY = click.option(
    "--key",
    "-k",
    "key",
    required=True,
    help="API Key of user in Axonius instance.",
    metavar="KEY",
    prompt="API Key of user in Axonius instance",
    hide_input=True,
    show_envvar=True,
)
OPT_SECRET = click.option(
    "--secret",
    "-s",
    "secret",
    required=True,
    help="API Secret of user in Axonius instance.",
    metavar="SECRET",
    prompt="API Secret of user in Axonius instance",
    hide_input=True,
    show_envvar=True,
)
# FUTURE: error if os.path.sep in value
OPT_EXPORT_FILE = click.option(
    "--export-file",
    "-xf",
    "export_file",
    default="",
    help="Export to a file in export-path instead of printing to STDOUT.",
    show_envvar=True,
    show_default=True,
)
OPT_EXPORT_PATH = click.option(
    "--export-path",
    "-xp",
    "export_path",
    default=format(tools.path(obj=os.getcwd())),
    help="Path to create -xf/--export-file in (default is current working directory).",
    type=click.Path(exists=False, resolve_path=True),
    show_envvar=True,
)
OPT_EXPORT_FORMAT = click.option(
    "--export-format",
    "-xt",
    "export_format",
    default="json",
    help="Format to use for STDOUT (or -xf/--export-file if supplied).",
    type=click.Choice(["csv", "json"]),
    show_envvar=True,
    show_default=True,
)
OPT_EXPORT_OVERWRITE = click.option(
    "--export-overwrite",
    "-xo",
    "export_overwrite",
    default=False,
    help="Overwrite -xf/--export-file if exists.",
    is_flag=True,
    show_envvar=True,
)
OPT_EXPORT_DELIM = click.option(
    "--export-delim",
    "-xd",
    "export_delim",
    default="\n",
    help="Change the cell delimiter for CSV format from the default of carriage return.",
    show_envvar=True,
)
OPT_INCLUDE_SETTINGS = click.option(
    "--include-settings",
    "-is",
    "include_settings",
    help="Include settings in CSV export.",
    default=False,
    is_flag=True,
    show_envvar=True,
)
OPT_NO_ERROR = click.option(
    "--no-error",
    "-ne",
    "error",
    help="Continue processing rows even if an error happens.",
    default=True,
    is_flag=True,
    show_envvar=True,
)
OPT_QUERY = click.option(
    "--query",
    "-q",
    "query",
    help="Query built from Query Wizard to filter objects (empty returns all).",
    metavar="QUERY",
    show_envvar=True,
)
OPT_FIELDS = click.option(
    "--field",
    "-f",
    "fields",
    help="Fields (columns) to include in the format of adapter:field.",
    metavar="ADAPTER:FIELD",
    multiple=True,
    show_envvar=True,
)
OPT_FIELDS_DEFAULT = click.option(
    "--no-fields-default",
    "-nfd",
    "fields_default",
    default=True,
    help="Exclude default fields for this object type.",
    is_flag=True,
    show_envvar=True,
)
OPT_MAX_ROWS = click.option(
    "--max-rows", "-mr", "max_rows", help="Only return this many rows.", type=click.INT
)
OPT_GET_BY_VALUES = click.option(
    "--value",
    "-v",
    "values",
    help="Values to search for.",
    required=True,
    multiple=True,
    show_envvar=True,
)
OPT_GET_BY_POST_QUERY = click.option(
    "--query",
    "-q",
    "query",
    help="Query to add to the end of the query built to search for -v/--value.",
    default="",
    metavar="QUERY",
    show_envvar=True,
    show_default=True,
)
OPT_ROWS = click.option(
    "--rows",
    "-r",
    "rows",
    help="The rows in JSON format to process as a file or via stdin.",
    default="-",
    type=click.File(mode="r"),
    show_envvar=True,
    show_default=True,
)
OPT_WAIT_DELETE = click.option(
    "--wait",
    "-w",
    "wait",
    help="Wait this many seconds before deleting",
    default=30,
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
OPT_LABELS = click.option(
    "--label",
    "-l",
    "labels",
    help="Labels to process.",
    required=True,
    multiple=True,
    show_envvar=True,
)
