# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...tools import sysinfo


@click.command(name="sysinfo")
@click.pass_context
def cmd(ctx):
    """Print out system and python information."""
    info = sysinfo()
    for k, v in info.items():
        click.secho(f"{k}: {v}")
