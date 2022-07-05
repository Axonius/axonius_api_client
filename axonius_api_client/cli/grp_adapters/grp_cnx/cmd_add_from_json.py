# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxAddError
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, INPUT_FILE, add_options
from .grp_common import (
    EXPORT_FORMATS,
    OPT_EXPORT,
    OPT_IGNORE_UNKNOWNS,
    OPT_USE_SANE_DEFAULTS,
    OPTS_FLAGS,
    OPTS_NODE,
    OPTS_SHOWS,
)
from .parsing import get_show_data, parse_config

OPTIONS = [
    *AUTH,
    *OPTS_NODE,
    *OPTS_SHOWS,
    *OPTS_FLAGS,
    OPT_USE_SANE_DEFAULTS,
    OPT_IGNORE_UNKNOWNS,
    OPT_EXPORT,
    INPUT_FILE,
]


@click.command(name="add-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    input_file,
    export_format,
    adapter_node,
    adapter_name,
    tunnel,
    save_and_fetch,
    active,
    show_schemas,
    show_defaults,
    use_sane_defaults,
    ignore_unknowns,
):
    """Add a connection from a JSON file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
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

    config = ctx.obj.read_stream_json(stream=input_file, expect=dict)
    config = parse_config(
        schemas=schemas,
        adapter_name=adapter_name,
        config=config,
        use_sane_defaults=use_sane_defaults,
        prompt_for_optional=False,
        prompt_for_default=False,
        prompt_for_missing_required=False,
        ignore_unknowns=ignore_unknowns,
    )

    had_error = False
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        try:
            data = client.adapters.cnx.add(
                adapter_name=adapter_name,
                adapter_node=adapter_node,
                tunnel=tunnel,
                save_and_fetch=save_and_fetch,
                active=active,
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
