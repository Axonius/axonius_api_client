# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import ABORT, AUTH, INPUT_FILE, add_options, get_option_help
from .cmd_add_from_json import handle_updates
from .grp_common import OPT_OVERWRITE, OPTS_EXPORT

OPTIONS = [
    *AUTH,
    *OPTS_EXPORT,
    ABORT,
    OPT_OVERWRITE,
    INPUT_FILE,
    get_option_help(choices=["auth", "query", "selectfields", "wizard_csv"]),
]


@click.command(name="add-from-wiz-csv", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    input_file,
    abort,
    overwrite,
    export_format,
    table_format,
    help_detailed,
):
    """Add saved queries from a Wizard CSV file."""
    content = ctx.obj.read_stream(stream=input_file)
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror, abort=True):
        rows = apiobj.wizard_csv.parse(content=content)
        file_name = getattr(input_file, "name", input_file)
        ctx.obj.echo_ok(f"Parsed {len(rows)} Saved Queries from {file_name}")

    handle_updates(
        rows=rows,
        input_file=input_file,
        ctx=ctx,
        apiobj=apiobj,
        abort=abort,
        overwrite=overwrite,
        export_format=export_format,
        table_format=table_format,
        parse_method=apiobj.saved_query.build_add_model,
    )
