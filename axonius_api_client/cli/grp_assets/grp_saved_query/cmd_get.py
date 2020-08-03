# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import re

from ....tools import listify
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMAT, handle_export

OPTIONS = [
    *AUTH,
    EXPORT_FORMAT,
    click.option(
        "--name",
        "-n",
        "names",
        help="Names of saved queries",
        multiple=True,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--name-regex",
        "-nr",
        "names_regex",
        help="Regular expressions of names of saved queries",
        multiple=True,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--tag",
        "-t",
        "tags",
        help="Tags of saved queries",
        required=False,
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, names, names_regex, tags, **kwargs):
    """Get saved queries."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = apiobj.saved_query.get(**kwargs)
        for name in listify(names):
            rows = [x for x in rows if x["name"] == name]
        for tag in listify(tags):
            rows = [x for x in rows if tag in listify(x.get("tags", []))]
        for name_regex in listify(names_regex):
            rows = [x for x in rows if re.search(name_regex, x["name"], re.I)]

    handle_export(ctx=ctx, rows=rows, export_format=export_format)
