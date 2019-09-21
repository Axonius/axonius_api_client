# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click


class SplitEquals(click.ParamType):
    """Pass."""

    name = "split_equals"

    def convert(self, value, param, ctx):
        """Pass."""
        split = value.split("=", 1)

        if len(split) != 2:
            msg = "Need an '=' in --{p} with value {v!r}"
            msg = msg.format(p=param.name, v=value)
            self.fail(msg, param, ctx)

        return [x.strip() for x in split]


class AliasedGroup(click.Group):
    """Pass."""

    def get_command(self, ctx, cmd_name):
        """Pass."""
        rv = click.Group.get_command(self, ctx, cmd_name)

        if rv is not None:
            return rv

        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]

        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])

        msg = "Too many matches for {v!r}: {matches}"
        msg = msg.format(v=cmd_name, matches=", ".join(sorted(matches)))
        ctx.fail(msg)
