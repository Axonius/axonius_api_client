# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click
import tabulate

from .. import DEFAULT_PATH
from ..constants.api import MAX_PAGE_SIZE, TABLE_FORMAT
from ..tools import coerce_int
from . import context


def build_filter_opt(value_type: str):
    """Pass."""
    short_opt = "".join([x[0] for x in value_type.split("_")])
    long_opt = value_type.replace("_", "-")
    camel = " ".join(x.title() for x in value_type.split("_"))
    return click.option(
        f"--filter-{long_opt}",
        f"-f{short_opt}",
        f"{value_type}",
        help=f"Filter for records with matching {camel} (~ prefix for regex!) (multiple)",
        multiple=True,
        show_envvar=True,
        show_default=True,
        required=False,
    )


def add_options(options):
    """Pass."""

    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def int_callback(ctx, param, value):
    """Pass."""
    return coerce_int(value)


def help_callback(ctx, param, value):
    """Pass."""
    if value:
        from .helps import HELPSTRS

        helpstr = HELPSTRS[value]
        if callable(helpstr):
            helpstr = helpstr(ctx=ctx, param=param, value=value)
        click.secho(helpstr, err=True, fg="blue")
        ctx.exit(0)


def get_option_help(choices):
    """Pass."""
    return click.option(
        "--help-detailed",
        "help_detailed",
        help="Show detailed help and exit",
        type=click.Choice(choices),
        callback=help_callback,
        is_eager=True,
    )


def get_option_fields_default(default=True):
    """Pass."""
    return click.option(
        "--fields-default/--no-fields-default",
        "-fd/-nfd",
        "fields_default",
        default=default,
        help="Include the default fields defined in the API library",
        is_flag=True,
        show_envvar=True,
        show_default=True,
    )


URL = click.option(
    "--url",
    "-u",
    "url",
    required=True,
    help="URL of an Axonius instance",
    metavar="URL",
    prompt="URL",
    show_envvar=True,
    show_default=True,
)


AUTH = [
    URL,
    click.option(
        "--key",
        "-k",
        "key",
        required=True,
        help="API Key (or username if credentials=True) of user in an Axonius instance",
        metavar="KEY",
        prompt="API Key (or username if credentials=True) of user",
        hide_input=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--secret",
        "-s",
        "secret",
        required=True,
        help="API Secret (or password if credentials=True) of user in an Axonius instance",
        metavar="SECRET",
        prompt="API Secret (or password if credentials=True) of user",
        hide_input=True,
        show_envvar=True,
        show_default=True,
    ),
]

SQ_NAME = click.option(
    "--name",
    "-n",
    "name",
    help="Name of saved query",
    required=True,
    show_envvar=True,
    show_default=True,
)

QUERY = [
    click.option(
        "--query",
        "-q",
        "query",
        help="Query built from the Query wizard in the GUI",
        metavar="QUERY",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--query-file",
        "-qf",
        "query_file",
        help="Path to a file to override --query",
        type=click.File(),
        metavar="QUERY_FILE",
        show_envvar=True,
        show_default=True,
    ),
]

FIELDS_SELECT_BASE = [
    click.option(
        "--field",
        "-f",
        "fields",
        help="Fields to include in the format of adapter:field (multiples)",
        metavar="ADAPTER:FIELD",
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--field-regex",
        "-fr",
        "fields_regex",
        help="Regular expressions of fields to include (multiples)",
        metavar="ADAPTER_REGEX:FIELD_REGEX",
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--fields-regex-root-only/--no-fields-regex-root-only",
        "-frro/-nfrro",
        "fields_regex_root_only",
        help="Only include root fields for --field-regex",
        is_flag=True,
        default=True,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--field-fuzzy",
        "-ff",
        "fields_fuzzy",
        help="Fuzzy matching of fields to include (multiples)",
        metavar="ADAPTER:FIELD",
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--fields-root",
        "-fro",
        "fields_root",
        help="Select all root fields for a given adapter (PERFORMANCE HIT!)",
        metavar="ADAPTER",
        default=None,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
]

FIELDS_SELECT = [
    *FIELDS_SELECT_BASE,
    click.option(
        "--fields-error/--no-fields-error",
        "-fer/-nfer",
        "fields_error",
        help="Throw errors for invalid fields supplied in --field",
        is_flag=True,
        default=True,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
]
OPT_EXPORT_FILE = click.option(
    "--export-file",
    "-xf",
    "export_file",
    default="",
    help="File to send data to",
    show_envvar=True,
    show_default=True,
    metavar="PATH",
)
OPT_EXPORT_PATH = click.option(
    "--export-path",
    "-xp",
    "export_path",
    default=DEFAULT_PATH,
    help="If --export-file supplied, the directory to write --export_file to",
    type=click.Path(exists=False, resolve_path=True),
    show_envvar=True,
    show_default=True,
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
OPT_EXPORT_BACKUP = click.option(
    "--export-backup/--no-export-backup",
    "-xb/-nxb",
    "export_backup",
    default=False,
    help="If --export-file supplied and it exists, rename it with datetime",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)

EXPORT = [OPT_EXPORT_FILE, OPT_EXPORT_PATH, OPT_EXPORT_OVERWRITE]


PAGING = [
    click.option(
        "--max-rows",
        "max_rows",
        help="Stop fetching assets after this many rows have been received",
        type=click.INT,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--max-pages",
        "max_pages",
        help="Stop fetching assets after this many pages have been received",
        type=click.INT,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--page-size",
        "page_size",
        help="Number of assets to fetch per page",
        default=MAX_PAGE_SIZE,
        type=click.INT,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--row-start",
        "row_start",
        help="Start fetching from row N",
        default=0,
        type=click.INT,
        show_envvar=True,
        show_default=True,
        hidden=True,
    ),
    click.option(
        "--page-start",
        "page_start",
        help="Start fetching from page N of --page-size",
        default=0,
        type=click.INT,
        show_envvar=True,
        show_default=True,
        hidden=True,
    ),
    click.option(
        "--page-sleep",
        "page_sleep",
        default=0,
        type=click.INT,
        help="Seconds to wait in between each fetch of a page",
        show_envvar=True,
        show_default=True,
    ),
]

SPLIT_CONFIG_OPT = click.option(
    "--config",
    "-c",
    "config",
    help="Configuration keys in the form of key=value (multiples)",
    type=context.SplitEquals(),
    multiple=True,
    show_envvar=True,
    show_default=True,
    required=False,
)

SPLIT_CONFIG_REQ = click.option(
    "--config",
    "-c",
    "config",
    help="Configuration keys in the form of key=value (multiples)",
    type=context.SplitEquals(),
    multiple=True,
    show_envvar=True,
    show_default=True,
    required=True,
)

INPUT_FILE = click.option(
    "--input-file",
    "-if",
    "input_file",
    help="File to read (from path or piped via STDIN)",
    default="-",
    type=click.File(mode="r"),
    show_envvar=True,
    show_default=True,
)
NODE = [
    click.option(
        "--node-name",
        "-nn",
        "node",
        default=None,
        show_envvar=True,
        show_default=True,
        help="Node name (will default to core instance if not supplied)",
    ),
    click.option(
        "--name",
        "-n",
        "name",
        required=True,
        show_envvar=True,
        show_default=True,
        help="Adapter name",
    ),
]


ABORT = click.option(
    "--abort/--no-abort",
    "-a/-na",
    "abort",
    help="Stop on errors",
    required=False,
    default=True,
    show_envvar=True,
    show_default=True,
)

TABLE_FMT = click.option(
    "--table-format",
    "-tf",
    "table_format",
    default=TABLE_FORMAT,
    help="Base format to use for --export-format=table",
    type=click.Choice(tabulate.tabulate_formats),
    show_envvar=True,
    show_default=True,
    hidden=False,
)
