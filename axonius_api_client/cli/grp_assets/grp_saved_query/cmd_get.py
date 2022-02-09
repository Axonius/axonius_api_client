# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import re

from ....tools import listify
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPTS_EXPORT

OPTIONS = [
    *AUTH,
    *OPTS_EXPORT,
    click.option(
        "--name",
        "-n",
        "names",
        help="Names or UUID's of saved queries (multiple)",
        multiple=True,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--name-regex",
        "-nr",
        "names_regex",
        help="Regular expressions of names of saved queries (multiple)",
        multiple=True,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--tag",
        "-t",
        "tags",
        help="Tags of saved queries (multiple)",
        required=False,
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, names, names_regex, tags):
    """Get saved queries."""

    def is_match(row):
        return (
            (names and not any([x in [row.name, row.uuid] for x in names]))
            or (tags and not any([x in listify(row.tags) for x in tags]))
            or (names_regex and not any([x.search(row.name) for x in names_regex]))
        )

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        names = listify(names)
        tags = listify(tags)
        names_regex = listify(names_regex)
        ctx.obj.echo_ok(f"Filters: names={names}, tags={tags}, names_regex={names_regex}")
        names_regex = [re.compile(x, re.I) for x in names_regex]
        data = apiobj.saved_query.get(as_dataclass=True)
        ctx.obj.echo_ok(f"Saved Queries fetched: {len(data)}")
        data = [x for x in data if not is_match(x)]
        ctx.obj.echo_ok(f"Saved Queries matching filters: {len(data)}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
