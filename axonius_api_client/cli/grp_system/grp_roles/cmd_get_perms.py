# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

OPTIONS = [*AUTH]


@click.command(name="get-perms", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret):
    """Get the permission categories and actions."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system_roles.cat_actions

    cats = data["categories"]
    cat_actions = data["actions"]

    for cat, actions in cat_actions.items():
        cat_desc = cats[cat]
        click.secho(f"Category Description: {cat_desc!r}, Name: {cat!r}")
        for action, action_desc in actions.items():
            click.secho(f"  Action Description: {action_desc}, Name: {action!r}")
