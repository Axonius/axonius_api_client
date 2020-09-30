# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, INPUT_FILE, add_options, get_option_help
from .grp_common import ABORT, EXPORT_FORMAT, OVERWRITE, check_sq_exist, handle_export

OPTIONS = [
    *AUTH,
    EXPORT_FORMAT,
    ABORT,
    OVERWRITE,
    INPUT_FILE,
    get_option_help(choices=["auth", "query", "selectfields", "wizard_csv"]),
]


@click.command(name="add-from-wiz-csv", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file, abort, overwrite, export_format, **kwargs):
    """Add saved queries from a Wizard CSV file."""
    content = ctx.obj.read_stream(stream=input_file)
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror, abort=abort):
        sqs = apiobj.wizard_csv.parse(content=content)
        print(len(sqs))
        for sq in sqs:
            name = sq["name"]
            check_sq_exist(ctx=ctx, apiobj=apiobj, name=name, overwrite=overwrite)
            row = apiobj.saved_query.add(**sq)
            ctx.obj.echo_ok(f"Successfully created saved query: {name}")
            handle_export(ctx=ctx, rows=row, export_format=export_format)

    ctx.exit(0)
