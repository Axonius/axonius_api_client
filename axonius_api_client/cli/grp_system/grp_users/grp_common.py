# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
# from ....constants import DEFAULT_PERM, PERM_SETS, VALID_PERMS
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


def handle_export(ctx, data, export_format, **kwargs):
    """Get roles."""
    if export_format == "json":
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "str":
        for item in listify(data):
            is_admin = item.get("admin", False)
            first_name = item["first_name"]
            last_name = item["last_name"]
            perms = item.get("permissions", {})
            source = item["source"]
            user_name = item["user_name"]

            click.secho("\n---------------------------------------")
            click.secho(f"User Name: {user_name}")
            click.secho(f"{user_name} -- Is Admin: {is_admin}")
            click.secho(f"{user_name} -- First Name: {first_name}")
            click.secho(f"{user_name} -- Last Name: {last_name}")
            click.secho(f"{user_name} -- Source: {source}")
            for k, v in perms.items():
                click.secho(f"{user_name} -- {k} permission: {v}")
        ctx.exit(0)

    ctx.exit(1)
