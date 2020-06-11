# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import join_kv, json_dump, listify
from ...context import click

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json", "str"]),
    help="Format of to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)

ROLE_NAME = click.option(
    "--name",
    "-n",
    "name",
    help="Name of role",
    required=True,
    show_envvar=True,
    show_default=True,
)

ALLOW = click.option(
    "--allow",
    "-a",
    "allow",
    help="Regex of permissions to allow",
    required=True,
    show_envvar=True,
    show_default=True,
)

DENY = click.option(
    "--deny",
    "-d",
    "deny",
    help="Regex of permissions to deny",
    required=True,
    show_envvar=True,
    show_default=True,
)

DEFAULT = click.option(
    "--default-allow/--default-deny",
    "-da/-dd",
    "default",
    help="Default access to apply to unspecified permissions",
    required=False,
    default=False,
    show_envvar=True,
    show_default=True,
)


def handle_export(ctx, data, export_format, **kwargs):
    """Get roles."""
    if export_format == "json":
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "str":
        for item in listify(data):
            for perm in item["perms"]:
                perm = {k.title(): v for k, v in perm.items()}
                click.secho(", ".join(join_kv(obj=perm)))

            click.secho("\n")

        ctx.exit(0)

    ctx.exit(1)
