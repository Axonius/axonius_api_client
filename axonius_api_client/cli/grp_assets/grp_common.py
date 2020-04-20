# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import re

from ... import constants, tools
from ..context import click


def get_handler(ctx, url, key, secret, method, values=None, **kwargs):
    """Handle all of the get* commands."""
    query_file = kwargs.pop("query_file", None)
    if query_file:
        kwargs["query"] = query_file.read().strip()

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    method = method.replace("-", "_")
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)
    apimethod = getattr(apiobj, method)

    if values:
        get_first = isinstance(values, constants.LIST) and len(values) == 1

        if method == "get_by_subnet":
            kwargs.pop("value_regex", None)
            get_first = True

        kwargs["value"] = values[0] if get_first else values

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        apimethod(**kwargs)


def count_handler(ctx, url, key, secret, method, **kwargs):
    """Pass."""
    query_file = kwargs.pop("query_file", None)
    if query_file:
        kwargs["query"] = query_file.read().strip()

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    method = method.replace("-", "_")
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)
    apimethod = getattr(apiobj, method)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_data = apimethod(**kwargs)

    click.secho(format(raw_data))


def fields_handler(
    ctx, url, key, secret, method, adapter_re, field_re, field_key, schema_type, **kwargs
):
    """Handle fields group."""
    p_grp = ctx.parent.command.name

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = getattr(client, p_grp)
    apimethod = getattr(apiobj.fields, method)

    are = re.compile(adapter_re, re.I)
    fre = re.compile(field_re, re.I)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_fields = apimethod()

    amatches = {k: v for k, v in raw_fields.items() if are.search(k)}

    if not amatches:
        ctx.obj.echo_error(
            "No adapters found matching {!r}, valids: {}".format(
                adapter_re, list(raw_fields)
            )
        )

    fmatches = {k: {} for k in amatches}

    for adapter, schemas in amatches.items():
        for field, schema in schemas.items():
            fmatch = schema[field_key]
            if fre.search(fmatch):
                fmatches[adapter][field] = schema

    if schema_type == "basic":
        basic_keys = ["name_qual", "column_title", "type_norm"]
        basic = {k: {} for k in fmatches}
        for adapter, schemas in fmatches.items():
            for field, schema in schemas.items():
                basic[adapter][field] = {
                    k: v for k, v in schema.items() if k in basic_keys
                }
        click.secho(tools.json_dump(basic))
        ctx.exit(0)

    click.secho(tools.json_dump(fmatches))
