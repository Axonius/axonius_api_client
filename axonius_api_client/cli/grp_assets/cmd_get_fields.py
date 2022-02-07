# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import re
from typing import Optional, Pattern

from ...constants.fields import AGG_ADAPTER_NAME
from ...parsers.tables import tablize
from ...tools import json_dump
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options


def export_json_full(data, **kwargs):
    """Pass."""
    return json_dump(data)


def export_json(data, **kwargs):
    """Pass."""
    keys = {
        "adapter_name": "Adapter",
        "column_name": "Name",
        "column_title": "Title",
        "is_complex": "Is complex",
        "is_root": "Is root",
        "type_norm": "Normalized Type",
        "name_qual": "Fully Qualified Name",
    }
    data = [{k: v for k, v in x.items() if k in keys} for x in data]
    return json_dump(data)


def export_str(data, **kwargs):
    """Pass."""
    return "\n".join([x["column_name"] for x in data])


def export_table(data, **kwargs):
    """Pass."""
    keys = {
        "adapter_name": "Adapter",
        "column_name": "Name",
        "column_title": "Title",
        "type_norm": "Normalized Type",
    }
    data = [{keys[k]: v for k, v in x.items() if k in keys} for x in data]
    return tablize(value=data)


EXPORT_FORMATS: dict = {
    "json": export_json,
    "json-full": export_json_full,
    "str": export_str,
    "table": export_table,
}


class Defaults:
    """Pass."""

    root_only = False
    field_key = "name_qual"
    field_re = ".*"
    adapter_re = ".*"
    include_simple = True
    include_complex = True
    include_agg = True
    export_format = "str"


class Patterns:
    """Pass."""

    adapter_re: Optional[Pattern] = None
    field_re: Optional[Pattern] = None


OPTIONS = [
    *AUTH,
    click.option(
        "--adapter-re",
        "-ar",
        "adapter_re",
        default=Defaults.adapter_re,
        help="Only fetch fields for adapters matching this regex",
        metavar="REGEX",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--field-re",
        "-fr",
        "field_re",
        default=Defaults.field_re,
        help="Only fetch fields matching this regex",
        metavar="REGEX",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--field-key",
        "-fk",
        "field_key",
        default=Defaults.field_key,
        help="Which field key to match against for --field-re",
        type=click.Choice(["name_qual", "name", "name_base", "column_title", "column_name"]),
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--root-only/--no-root-only",
        "-ro/-nro",
        "root_only",
        default=Defaults.root_only,
        is_flag=True,
        help="Only show root fields",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--include-simple/--no-include-simple",
        "-is/-nis",
        "include_simple",
        default=Defaults.include_simple,
        is_flag=True,
        help="Include simple fields",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--include-complex/--no-include-complex",
        "-ic/-nic",
        "include_complex",
        default=Defaults.include_complex,
        is_flag=True,
        help="Include complex fields",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--include-agg/--no-include-agg",
        "-ia/-nia",
        "include_agg",
        default=Defaults.include_agg,
        is_flag=True,
        help="Include aggregated fields",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--export-format",
        "-xf",
        "export_format",
        type=click.Choice(list(EXPORT_FORMATS)),
        help="Control how much schema information to return",
        default=Defaults.export_format,
        show_envvar=True,
        show_default=True,
    ),
]


def is_match(
    schema: dict,
    adapter_re: str = Defaults.adapter_re,
    root_only: bool = Defaults.root_only,
    include_agg: bool = Defaults.include_agg,
    include_complex: bool = Defaults.include_complex,
    include_simple: bool = Defaults.include_simple,
    field_re: str = Defaults.field_re,
    field_key: str = Defaults.field_key,
) -> bool:
    """Pass."""

    def check_re(value, key):
        return False if hasattr(value, "search") and not value.search(schema[key]) else True

    if not check_re(adapter_re, "adapter_name") or not check_re(field_re, field_key):
        return False

    if root_only and not schema["is_root"]:
        return False

    if not include_agg and schema["is_agg"] and not schema["adapter_name"] == AGG_ADAPTER_NAME:
        return False

    if not include_complex and schema["is_complex"]:
        return False

    if not include_simple and not schema["is_complex"]:
        return False

    if not schema.get("selectable"):
        return False

    return True


def get_matches(data, **kwargs):
    """Pass."""

    def compile_re(key):
        value = kwargs.get(key)
        if isinstance(value, str) and value.strip():
            kwargs[key] = re.compile(value, re.I)

    compile_re("adapter_re")
    compile_re("field_re")

    return [x for schemas in data.values() for x in schemas if is_match(schema=x, **kwargs)]


@click.command(name="get-fields", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, help_detailed=None, **kwargs):
    """Get the available fields (columns) for assets."""
    p_grp = ctx.parent.command.name
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = getattr(client, p_grp)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.fields.get()
    matches = get_matches(data=data, **kwargs)
    click.secho(EXPORT_FORMATS[export_format](data=matches))
    ctx.exit(0)
