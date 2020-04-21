# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....constants import DEFAULT_PERM, PERM_SETS, VALID_PERMS
from ....tools import json_dump, listify
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

PERMS = [
    click.option(
        f"--{x.lower()}",
        f"-{x.lower()[:4]}",
        f"{x.lower()}",
        help=f"Permission level for {x}",
        type=click.Choice(VALID_PERMS),
        required=False,
        default=DEFAULT_PERM,
        show_envvar=True,
        show_default=True,
    )
    for x in PERM_SETS
]


def handle_export(ctx, data, export_format, **kwargs):
    """Get roles."""
    if export_format == "json":
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "str":
        for item in listify(data):
            name = item["name"]
            perms = item["permissions"]

            click.secho("\n---------------------------------------")
            click.secho(f"Role Name: {name}")
            for k, v in perms.items():
                click.secho(f"{name} -- {k} permission: {v}")
        ctx.exit(0)

    ctx.exit(1)
