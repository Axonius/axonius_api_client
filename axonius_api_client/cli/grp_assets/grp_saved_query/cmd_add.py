# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....constants.api import GUI_PAGE_SIZES
from ...context import CONTEXT_SETTINGS, click
from ...grp_folders.grp_options import OPTS_OBJECT_CREATE
from ...options import (
    AUTH,
    FIELDS_SELECT_BASE,
    QUERY,
    add_options,
    get_option_fields_default,
    get_option_help,
    int_callback,
)
from ..grp_common import WIZ, load_wiz
from .grp_common import EXPORT_FORMATS, OPTS_EXPORT

OPTIONS = [
    get_option_help(choices=["auth", "query", "selectfields", "wizard"]),
    *AUTH,
    *OPTS_EXPORT,
    *QUERY,
    *WIZ,
    click.option(
        "--tag",
        "-t",
        "tags",
        help="Tags to set for saved query (multiple)",
        multiple=True,
        show_envvar=True,
        show_default=True,
        required=False,
    ),
    click.option(
        "--description",
        "-d",
        "description",
        help="Description to set on saved query",
        show_envvar=True,
        show_default=True,
        default=None,
        required=False,
    ),
    *FIELDS_SELECT_BASE,
    get_option_fields_default(default=True),
    click.option(
        "--sort-field",
        "-sf",
        "sort_field",
        help="Column to sort data on.",
        metavar="ADAPTER:FIELD",
        show_envvar=True,
        show_default=True,
        default=None,
        required=False,
    ),
    click.option(
        "--sort-descending/--no-sort-descending",
        "-sd/-nsd",
        "sort_descending",
        default=True,
        help="Sort --sort-field descending.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        required=False,
    ),
    click.option(
        "--gui-page-size",
        "-gps",
        default=str(GUI_PAGE_SIZES[0]),
        help="Number of rows to show per page in GUI.",
        type=click.Choice([str(x) for x in GUI_PAGE_SIZES]),
        callback=int_callback,
        show_envvar=True,
        show_default=True,
        required=False,
    ),
    click.option(
        "--private/--no-private",
        "-pr/-npr",
        "private",
        default=False,
        help="Set as private.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        required=False,
    ),
    click.option(
        "--always-cached/--no-always-cached",
        "-ac/-nac",
        "always_cached",
        default=False,
        help="Set as always cached.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        required=False,
    ),
    click.option(
        "--asset-scope/--no-asset-scope",
        "-as/-nas",
        "asset_scope",
        default=False,
        help="Set as an asset scope query.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        required=False,
    ),
    click.option(
        "--name",
        "-n",
        "name",
        help="Name of saved query",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    *OPTS_OBJECT_CREATE,
]


@click.command(name="add", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, wizard_content, **kwargs):
    """Add a saved query."""
    query_file = kwargs.pop("query_file", None)
    kwargs["query"] = query_file.read().strip() if query_file else kwargs.get("query")
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        kwargs = load_wiz(apiobj=apiobj, wizard_content=wizard_content, exprs=True, kwargs=kwargs)
        data = apiobj.saved_query.add(as_dataclass=True, **kwargs)

    ctx.obj.echo_ok(f"Successfully created saved query: {data.name}")
    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
