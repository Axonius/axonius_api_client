# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...features import Features
from ..context import CONTEXT_SETTINGS, click
from ..options import add_options

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

    def is_match(obj):
        return True if not feature_name else feature_name == obj.name

    data = Features.get_features()
    barrier = "*" * 60
    content = (
        [f"{barrier}\n{x}" for x in data if is_match(x)]
        if data
        else ["No features currently available"]
    )
    content = content or [f"No features matching name {feature_name!r}"]
    click.secho("\n".join(content))
    ctx.exit(0)
