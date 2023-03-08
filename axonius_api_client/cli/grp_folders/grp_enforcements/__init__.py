# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup, load_cmds


@click.group(cls=AliasedGroup)
def enforcements():
    """Group: Work with folders for Enforcements."""


load_cmds(path=__file__, package=__package__, group=enforcements)

# XXX
"""
axonshell folders enforcements create --path "/Shared Queries/t1"
axonshell folders enforcements delete --path "/Shared Queries/t1" --confirm
axonshell folders enforcements delete --path "/Shared Queries/t1" --prompt
axonshell folders enforcements get
axonshell folders enforcements get --path "blah"
axonshell folders enforcements move --path "/Shared Queries/t1" --value "Shared Queries/t2"
axonshell folders enforcements rename --path "/Shared Queries/t1" --value "t2"
axonshell folders enforcements search-objects --path "/Shared Queries/t1" --value '~test'
axonshell folders enforcements search-objects-copy --path --search --target
axonshell folders enforcements search-objects-delete --path --search --target
axonshell folders enforcements search-objects-move --path --search --target
"""
