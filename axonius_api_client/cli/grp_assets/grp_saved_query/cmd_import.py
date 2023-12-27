# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, NODE, add_options

OPTIONS = [
    *AUTH,
    click.option(
        "--input-file",
        "-if",
        "input_file",
        help="File to upload (from path or piped via STDIN)",
        default="-",
        type=click.File(mode="r"),
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="import", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file, **kwargs):
    """Import saved queries from a previously exported file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    stream_name = format(getattr(input_file, "name", input_file))

    kwargs["file_name"] = stream_name
    kwargs["field_name"] = "field_name.json"
    kwargs["file_content"] = ctx.obj.read_stream(stream=input_file)
    kwargs["file_content_type"] = "application/json"

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        upload_results = apiobj.saved_query.saved_query_import(**kwargs)
        ctx.obj.echo_ok(f"Import results: "
                        f"failed_queries={upload_results.failed_queries} "
                        f"inserted_queries={upload_results.inserted_queries} "
                        f"replaced_queries={upload_results.replaced_queries}")

    ctx.obj.echo_ok("File uploaded")
