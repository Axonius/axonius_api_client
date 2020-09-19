# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import dt_parse, json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

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

OPTIONS = [
    *AUTH,
    EXPORT,
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get instances information."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.instances.get()

    if export_format == "json":
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "str":
        for item in data:
            ips = ", ".join(item["ips"])
            last_seen = str(dt_parse(item["last_seen"]))
            name = item["node_name"]
            is_env = item["use_as_environment_name"]
            node_id = item["node_id"]
            hostname = item["hostname"]
            is_core = item["is_master"]
            status = item["status"]

            click.secho("\n---------------------------------------")
            click.secho(f"Node Name: {name}")
            click.secho(f"{name} - Node ID: {node_id}")
            click.secho(f"{name} - Hostname: {hostname}")
            click.secho(f"{name} - IP: {ips}")
            click.secho(f"{name} - Is Core: {is_core}")
            click.secho(f"{name} - Status: {status}")
            click.secho(f"{name} - Last Seen: {last_seen}")
            click.secho(f"{name} - Is Environment Banner: {is_env}")
        ctx.exit(0)

    ctx.exit(1)
