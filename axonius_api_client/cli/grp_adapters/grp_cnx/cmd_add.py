# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxAddError
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, NODE_CNX, SPLIT_CONFIG_OPT, add_options
from .grp_common import EXPORT, handle_export, prompt_schema

OPTIONS = [
    *AUTH,
    EXPORT,
    *NODE_CNX,
    click.option(
        "--prompt-optional / --no-prompt-optional",
        "-po / -npo",
        "prompt_optional",
        help="Prompt for optional items that are not supplied.",
        is_flag=True,
        default=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--prompt-default / --no-prompt-default",
        "-pd / -npd",
        "prompt_default",
        help="Prompt for items that have a default.",
        is_flag=True,
        default=True,
        show_envvar=True,
        show_default=True,
    ),
    SPLIT_CONFIG_OPT,
]


@click.command(name="add", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    config,
    export_format,
    prompt_optional,
    prompt_default,
    adapter_name,
    adapter_node,
    **kwargs,
):  # noqa
    """Add a connection to an adapter."""

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    config = dict(config)
    kwargs["kwargs_config"] = config

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        adapter = client.adapters.get_by_name(name=adapter_name, node=adapter_node)

    schemas = list(adapter["schemas"]["cnx"].values())
    schemas = reversed(sorted(schemas, key=lambda x: [x["required"], x["name"]]))

    for schema in schemas:
        prompt_schema(
            schema=schema,
            config=config,
            prompt_optional=prompt_optional,
            prompt_default=prompt_default,
            adapter_name=adapter_name,
        )

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        try:
            cnx_new = client.adapters.cnx.add(
                adapter_name=adapter_name, adapter_node=adapter_node, **config
            )
            ctx.obj.echo_ok(msg=f"Connection added successfully!")

        except CnxAddError as exc:
            ctx.obj.echo_error(msg=f"{exc}", abort=False)
            cnx_new = exc.cnx_new

    handle_export(ctx=ctx, rows=cnx_new, export_format=export_format)
