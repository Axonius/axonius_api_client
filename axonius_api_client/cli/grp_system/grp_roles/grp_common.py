# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import tabulate

from ....tools import json_dump, listify
from ...context import SplitEquals, click

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json", "str", "table"]),
    help="Format of to export data in",
    default="table",
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

PERMS = click.option(
    "--perm",
    "-p",
    "perms",
    help="""Permissions like $CATEGORY=$ACTION1,$ACTION2,...
    Can use $CATEGORY_NAME=all or $CATEGORY_NAME=none (MULTIPLE)""",
    required=True,
    show_envvar=True,
    show_default=True,
    type=SplitEquals(),
    multiple=True,
)


def handle_export(ctx, data, export_format, **kwargs):
    """Get roles."""
    if export_format == "json":
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "str":
        for item in listify(data):
            name = item["name"]
            perms = item["permissions_flat"]
            grants = []

            for category, actions in perms.items():
                if all([v is True for k, v in actions.items()]):
                    allows = "all"
                elif all([v is False for k, v in actions.items()]):
                    allows = "none"
                else:
                    allows = [k for k, v in actions.items() if v]
                    allows = ",".join(allows)
                grants.append(f"--perm {category}={allows!r}")

            grants = " ".join(grants)
            entry = f"--name {name!r} {grants}"
            click.secho(entry)

        ctx.exit(0)

    if export_format == "table":
        for item in listify(data):
            name = item["name"]
            last_updated = item["last_updated"]
            perms = item["permissions_flat_descriptions"]

            entry = [
                f"Role {name!r}",
                f"Updated: {last_updated}",
            ]
            entry = ", ".join(entry)
            table = tabulate.tabulate(perms, tablefmt="simple", headers="keys")
            click.secho(f"{entry}\n{table}\n")

        ctx.exit(0)
    ctx.exit(1)
