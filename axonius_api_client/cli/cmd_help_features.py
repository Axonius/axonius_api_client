# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..features import Features
from .context import CONTEXT_SETTINGS, click
from .options import add_options

OPTIONS = [
    click.option(
        "--feature-name",
        "feature_name",
        type=click.Choice([x.name for x in Features.get_features()]),
        help="Feature to get help for (will print all if not supplied)",
        default=None,
        required=False,
        show_envvar=True,
        show_default=True,
    )
]


@click.command(name="help-features", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, feature_name):
    """Help for using API Advanced Features."""
    features = Features.get_features()
    i = "*" * 60
    for feature in features:
        if feature_name and feature.name != features:
            continue
        click.secho(f"{i}\n{feature}")

    ctx.exit(0)
