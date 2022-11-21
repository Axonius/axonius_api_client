# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxAddError
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import (
    EXPORT_FORMATS,
    OPT_CNX_LABEL,
    OPT_EXPORT,
    OPT_SPLIT_CONFIG,
    OPTS_FLAGS,
    OPTS_NODE,
    OPTS_PROMPTS,
    OPTS_SHOWS,
)
from .parsing import get_show_data, parse_config

OPTIONS = [
    *AUTH,
    *OPTS_NODE,
    *OPTS_FLAGS,
    *OPTS_SHOWS,
    *OPTS_PROMPTS,
    OPT_CNX_LABEL,
    OPT_SPLIT_CONFIG,
    OPT_EXPORT,
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
    adapter_name,
    adapter_node,
    prompt_for_optional,
    prompt_for_default,
    save_and_fetch,
    active,
    show_schemas,
    show_defaults,
    use_sane_defaults,
    ignore_unknowns,
    connection_label,
    tunnel,
):
    """Add a connection from prompts or arguments."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    config = dict(config)
    config_label = config.pop("connection_label", None)
    connection_label = config_label or connection_label
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        adapter = client.adapters.get_by_name(name=adapter_name, node=adapter_node)
        cnxs = client.adapters.cnx._get(adapter_name=adapter["name_raw"])

    adapter_name = adapter["name"]
    adapter_node = adapter["node_name"]
    schemas = list(cnxs.schema_cnx.values())
    show_data = get_show_data(
        schemas=schemas,
        show_schemas=show_schemas,
        show_defaults=show_defaults,
        adapter_name=adapter_name,
        use_sane_defaults=use_sane_defaults,
    )
    if show_data:
        click.secho(show_data)
        ctx.exit(0)

    config = parse_config(
        schemas=schemas,
        adapter_name=adapter_name,
        config=config,
        use_sane_defaults=use_sane_defaults,
        prompt_for_optional=prompt_for_optional,
        prompt_for_default=prompt_for_default,
        ignore_unknowns=ignore_unknowns,
    )

    had_error = False
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        try:
            data = client.adapters.cnx.add(
                adapter_name=adapter_name,
                adapter_node=adapter_node,
                save_and_fetch=save_and_fetch,
                tunnel=tunnel,
                active=active,
                connection_label=connection_label,
                **config,
            )
            ctx.obj.echo_ok(msg="Connection added with no errors")
        except CnxAddError as exc:
            had_error = True
            ctx.obj.echo_error(msg=f"Connection added with error: {exc}", abort=False)
            data = exc.cnx_new
            if not ctx.obj.wraperror:  # pragma: no cover
                raise

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(100 if had_error else 0)
