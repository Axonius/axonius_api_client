# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxUpdateError
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import (
    EXPORT_FORMATS,
    OPT_EXPORT,
    OPT_ID_CNX,
    OPT_PROMPT_FOR_PREVIOUS,
    OPT_SPLIT_CONFIG,
    OPTS_FLAGS,
    OPTS_NODE,
    OPTS_PROMPTS,
    OPTS_SHOWS,
)
from .parsing import get_show_data, parse_config

OPTIONS_SHARED = [
    *AUTH,
    *OPTS_NODE,
    *OPTS_FLAGS,
    *OPTS_SHOWS,
    *OPTS_PROMPTS,
    OPT_PROMPT_FOR_PREVIOUS,
    OPT_EXPORT,
    OPT_ID_CNX,
]

OPTIONS = [
    *OPTIONS_SHARED,
    OPT_SPLIT_CONFIG,
]


@click.command(name="update-by-id", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, config, **kwargs):
    """Update a connection from arguments."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    config = dict(config)
    handle_update(ctx=ctx, client=client, config=config, **kwargs)


def handle_update(
    ctx,
    client,
    config,
    adapter_node,
    adapter_name,
    tunnel,
    cnx_id,
    save_and_fetch,
    active,
    export_format,
    show_schemas,
    show_defaults,
    use_sane_defaults,
    prompt_for_previous,
    prompt_for_optional,
    prompt_for_default,
    ignore_unknowns,
):
    """Pass."""
    if not config and not prompt_for_previous:  # pragma: no cover
        ctx.obj.echo_ok("No --config args supplied, forcing prompt_for_previous to True")
        prompt_for_previous = True

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        cnx = client.adapters.cnx.get_by_id(
            adapter_name=adapter_name, adapter_node=adapter_node, tunnel=tunnel, cnx_id=cnx_id
        )

    schemas = list(cnx["schemas"].values())
    show_data = get_show_data(
        schemas=schemas,
        show_schemas=show_schemas,
        show_defaults=show_defaults,
        adapter_name=adapter_name,
        use_sane_defaults=use_sane_defaults,
    )
    if show_data:  # pragma: no cover
        click.secho(show_data)
        ctx.exit(0)

    config = parse_config(
        schemas=schemas,
        adapter_name=adapter_name,
        config=config,
        config_previous=cnx["config"],
        use_sane_defaults=use_sane_defaults,
        prompt_for_previous=prompt_for_previous,
        prompt_for_optional=prompt_for_optional,
        prompt_for_default=prompt_for_default,
        ignore_unknowns=ignore_unknowns,
    )

    had_error = False

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        try:
            data = client.adapters.cnx.update_cnx(
                cnx_update=cnx, save_and_fetch=save_and_fetch, active=active, new_config=config
            )
            ctx.obj.echo_ok(msg="Connection updated with no errors")
        except CnxUpdateError as exc:  # pragma: no cover
            had_error = True
            ctx.obj.echo_error(msg=f"Connection updated with error: {exc}", abort=False)
            data = exc.cnx_new
            if not ctx.obj.wraperror:  # pragma: no cover
                raise

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(100 if had_error else 0)
