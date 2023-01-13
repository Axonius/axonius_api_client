# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import echo_ok, json_dump, path_write
from ..context import click


def export_json(data, **kwargs):
    """Pass."""
    return json_dump(data)


EXPORT_FORMATS: dict = {
    "json": export_json,
}


def handle_export(data, export_file, export_format="json", export_overwrite=False, **kwargs):
    """Pass."""
    data_dict = data.to_dict()
    output = EXPORT_FORMATS[export_format](data=data_dict)
    if export_file:
        export_path, data = path_write(obj=export_file, data=output, overwrite=export_overwrite)
        byte_len, backup_path = data
        echo_ok(
            f"Wrote dashboard spaces export in {export_format} format to: '{export_path}' "
            f"({byte_len} bytes)"
        )
    else:
        click.secho(output)
        echo_ok(f"Wrote dashboard spaces export in {export_format} format to STDOUT")
    echo_ok(f"Dashboard export info:\n{data}")


OPT_EXPORT_FILE = click.option(
    "--export-file",
    "-xf",
    "export_file",
    default="",
    help="File to send data to (STDOUT if not supplied)",
    show_envvar=True,
    show_default=True,
    metavar="PATH",
)
OPT_EXPORT_OVERWRITE = click.option(
    "--export-overwrite/--no-export-overwrite",
    "-xo/-nxo",
    "export_overwrite",
    default=False,
    help="If --export-file supplied and it exists, overwrite it",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
OPT_NAMES = click.option(
    "--name",
    "-n",
    "names",
    help="Names of Dashboard Spaces to export (use ~ prefix for regex) (multiple)",
    required=True,
    multiple=True,
    show_envvar=True,
    show_default=True,
)
OPT_ERROR_UNKNOWN = click.option(
    "--error-not-matched/--no-error-not-matched",
    "-enm/-nenm",
    "error_not_matched",
    default=True,
    help="Raise an error if any Dashboard Space in --value is not found",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
OPT_SEP = click.option(
    "--split-sep",
    "-sp",
    "split_sep",
    default=",",
    help="Seperator to use for delimiting multiple entries in a single --value",
    show_envvar=True,
    show_default=True,
)
OPT_POSTFIX_NAMES = click.option(
    "--postfix-names",
    "-pn",
    "postfix_names",
    help="str to add to names of all spaces, charts, and queries",
    default=None,
    required=False,
    multiple=False,
    show_envvar=True,
    show_default=True,
)
OPT_POSTFIX_NAMES_SPACES = click.option(
    "--postfix-names-spaces",
    "-pns",
    "postfix_names_spaces",
    help="str to add to names of all spaces",
    default=None,
    required=False,
    multiple=False,
    show_envvar=True,
    show_default=True,
)
OPT_POSTFIX_NAMES_CHARTS = click.option(
    "--postfix-names-charts",
    "-pnc",
    "postfix_names_charts",
    help="str to add to names of all charts",
    default=None,
    required=False,
    multiple=False,
    show_envvar=True,
    show_default=True,
)
OPT_POSTFIX_NAMES_QUERIES = click.option(
    "--postfix-names-queries",
    "-pnq",
    "postfix_names_queries",
    help="str to add to names of all queries",
    default=None,
    required=False,
    multiple=False,
    show_envvar=True,
    show_default=True,
)
OPT_EXCLUDE_NAMES = click.option(
    "--exclude-names",
    "-xn",
    "exclude_names",
    help=(
        "Exclude any spaces or charts that equal these names or match these patterns "
        "(use ~ prefix for regex) (multiple)"
    ),
    required=False,
    multiple=True,
    show_envvar=True,
    show_default=True,
)
OPT_EXCLUDE_NAMES_SPACES = click.option(
    "--exclude-names-spaces",
    "-xns",
    "exclude_names_spaces",
    help=(
        "Exclude any spaces that equal these names or match these patterns "
        "(use ~ prefix for regex) (multiple)"
    ),
    required=False,
    multiple=True,
    show_envvar=True,
    show_default=True,
)
OPT_EXCLUDE_NAMES_CHARTS = click.option(
    "--exclude-names-charts",
    "-xnc",
    "exclude_names_charts",
    help=(
        "Exclude any charts that equal these names or match these patterns "
        "(use ~ prefix for regex) (multiple)"
    ),
    required=False,
    multiple=True,
    show_envvar=True,
    show_default=True,
)
OPT_REPLACE = click.option(
    "--replace/--no-replace",
    "-r/-nr",
    "replace",
    default=False,
    help=(
        "If true and objects exist with same name, imported objects will replace existing objects. "
        "If False and objects exist with same name, imported objects will be renamed"
    ),
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
OPTS_POSTFIX = [
    OPT_POSTFIX_NAMES,
    OPT_POSTFIX_NAMES_SPACES,
    OPT_POSTFIX_NAMES_CHARTS,
    OPT_POSTFIX_NAMES_QUERIES,
]
OPTS_EXCLUDE = [
    OPT_EXCLUDE_NAMES,
    OPT_EXCLUDE_NAMES_SPACES,
    OPT_EXCLUDE_NAMES_CHARTS,
]
OPTS_EXPORT = [
    OPT_EXPORT_OVERWRITE,
    OPT_EXPORT_FILE,
]

OPT_SPACES = click.option(
    "--space",
    "-sp",
    "spaces",
    help="Names of Spaces include (use ~ prefix for regex) (multiple)",
    required=False,
    multiple=True,
    show_envvar=True,
    show_default=True,
)
OPT_CHARTS = click.option(
    "--chart",
    "-ch",
    "charts",
    help="Names of Charts to include (use ~ prefix for regex) (multiple)",
    required=False,
    multiple=True,
    show_envvar=True,
    show_default=True,
)
