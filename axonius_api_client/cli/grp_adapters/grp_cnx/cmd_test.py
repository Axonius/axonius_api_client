# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxTestError
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import OPT_SPLIT_CONFIG, OPTS_NODE, OPTS_PROMPTS, OPTS_SHOWS
from .parsing import get_show_data, parse_config

OPTIONS = [
    *AUTH,
    *OPTS_NODE,
    *OPTS_SHOWS,
    *OPTS_PROMPTS,
    OPT_SPLIT_CONFIG,
]


@click.command(name="test", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    config,
    adapter_name,
    adapter_node,
    tunnel,
    show_schemas,
    show_defaults,
    use_sane_defaults,
    prompt_for_optional,
    prompt_for_default,
    ignore_unknowns,
):
    """Test reachability for an adapter from prompts or arguments."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    config = dict(config)

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
    try:
        client.adapters.cnx.test(
            adapter_name=adapter_name,
            adapter_node=adapter_node,
            tunnel=tunnel,
            **config,
        )
        ctx.obj.echo_ok(msg="Connection tested with no errors")
    except CnxTestError as exc:
        had_error = True
        ctx.obj.echo_error(msg=f"Connection tested with error: {exc}", abort=False)
        if not ctx.obj.wraperror:  # pragma: no cover
            raise
    click.secho(f"Tested with configuration:\n{config}")
    ctx.exit(100 if had_error else 0)
