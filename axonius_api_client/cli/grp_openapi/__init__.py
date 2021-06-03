# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from axonius_api_client.cli.context import AliasedGroup
from . import cmd_get


@click.group(cls=AliasedGroup)
def openapi():
    """Group: Work with the OpenAPI YAML specification file."""


openapi.add_command(cmd_get.cmd)
