# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup, load_cmds


@click.group(cls=AliasedGroup)
def queries():
    """Group: Work with folders for Queries."""


load_cmds(path=__file__, package=__package__, group=queries)

# XXX
"""
axonshell folders queries create --path "/Shared Queries/t1"
axonshell folders queries delete --path "/Shared Queries/t1" --confirm
axonshell folders queries delete --path "/Shared Queries/t1" --prompt
axonshell folders queries get
axonshell folders queries get --path "blah"
axonshell folders queries move --path "/Shared Queries/t1" --value "Shared Queries/t2"
axonshell folders queries rename --path "/Shared Queries/t1" --value "t2"
axonshell folders queries search-objects --path "/Shared Queries/t1" --value '~test'
axonshell folders queries search-objects-copy --path --search --target
axonshell folders queries search-objects-delete --path --search --target
axonshell folders queries search-objects-move --path --search --target
"""
