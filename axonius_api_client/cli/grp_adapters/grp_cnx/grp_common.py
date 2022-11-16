# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....parsers.tables import tablize_cnxs, tablize_schemas
from ....tools import json_dump, listify
from ...context import SplitEquals, click
from .parsing import Defaults, Schema, SchemaBool


def export_json_full(data):
    """Pass."""
    return json_dump(data)


def export_json_config(data):
    """Pass."""

    def parse(obj):
        return obj["config"]

    data = [parse(x) for x in data] if isinstance(data, list) else parse(data)
    return json_dump(data)


def export_json(data):
    """Pass."""

    def parse(obj):
        obj.pop("schemas", None)
        return obj

    data = [parse(x) for x in data] if isinstance(data, list) else parse(data)
    return json_dump(data)


def export_table(data):
    """Pass."""
    data = listify(data)
    return tablize_cnxs(cnxs=data)


def export_table_schemas(data):
    """Pass."""

    def parse(obj):
        return obj["schemas"]

    schemas = parse(data[0]) if isinstance(data, list) else parse(data)
    return tablize_schemas(
        schemas=schemas,
        err=None,
        footer=True,
        orig=True,
        orig_width=20,
    )


def export_str(data):
    """Pass."""
    data = listify(data)
    tmpl = "{id}".format
    return "\n".join([tmpl(**x) for x in data])


def export_str_args(data):
    """Pass."""

    def parse(obj):
        tmpl = "--node-name {node_name!r} --name {adapter_name!r} --id {id!r}"
        if obj.get("tunnel_id"):
            tmpl += " --tunnel {tunnel_id!r}"
        return tmpl.format(**obj)

    data = listify(data)
    return "\n".join([parse(x) for x in data])


EXPORT_FORMATS: dict = {
    "json-full": export_json_full,
    "json-config": export_json_config,
    "json": export_json,
    "table": export_table,
    "table-schemas": export_table_schemas,
    "str": export_str,
    "str-args": export_str_args,
}

OPT_DELETE_ENTITIES = click.option(
    "--delete-entities / --no-delete-entities",
    "-de/-nde",
    "delete_entities",
    help="When deleting connection, also remove all assets created by connection.",
    is_flag=True,
    default=False,
    show_envvar=True,
    show_default=True,
)
OPT_SPLIT_CONFIG = click.option(
    "--config",
    "-c",
    "config",
    help=(
        "Configuration in the form of key=value "
        f"(value as {Schema.USE_DEFAULT} to use the default value) (multiples)"
    ),
    type=SplitEquals(),
    multiple=True,
    show_envvar=True,
    show_default=True,
    required=False,
)
OPT_IGNORE_UNKNOWNS = click.option(
    "--ignore-unknowns / --no-ignore-unknowns",
    "-iu/-niu",
    "ignore_unknowns",
    help="Do not error if unknown config keys supplied.",
    is_flag=True,
    default=Defaults.ignore_unknowns,
    show_envvar=True,
    show_default=True,
)
OPT_USE_SANE_DEFAULTS = click.option(
    "--use-sane-defaults / --no-use-sane-defaults",
    "-usd/-nusd",
    "use_sane_defaults",
    help=(
        "Use sane defaults from API Client"
        f" (will use {SchemaBool.SANE_DEFAULT} as default for boolean types)."
    ),
    is_flag=True,
    default=Defaults.use_sane_defaults,
    show_envvar=True,
    show_default=True,
)
OPT_PROMPT_FOR_DEFAULT = click.option(
    "--prompt-default / --no-prompt-default",
    "-pd / -npd",
    "prompt_for_default",
    help="Prompt for items that have a default.",
    is_flag=True,
    default=Defaults.prompt_for_default,
    show_envvar=True,
    show_default=True,
)
OPT_PROMPT_FOR_PREVIOUS = click.option(
    "--prompt-previous / --no-prompt-previous",
    "-pp / -npp",
    "prompt_for_previous",
    help="Prompt for all items in current connection config but not supplied in --config.",
    is_flag=True,
    default=Defaults.prompt_for_previous,
    show_envvar=True,
    show_default=True,
)
OPT_PROMPT_FOR_OPTIONALS = click.option(
    "--prompt-optional / --no-prompt-optional",
    "-po / -npo",
    "prompt_for_optional",
    help="Prompt for optional items that are not supplied.",
    is_flag=True,
    default=Defaults.prompt_for_optional,
    show_envvar=True,
    show_default=True,
)
OPT_SHOW_SCHEMAS = click.option(
    "--show-schemas / --no-show-schemas",
    "show_schemas",
    help="Print the schemas and exit.",
    is_flag=True,
    default=Defaults.show_schemas,
    show_envvar=True,
    show_default=True,
)
OPT_SHOW_DEFAULTS = click.option(
    "--show-defaults / --no-show-defaults",
    "show_defaults",
    help="Print the schema defaults and sane defaults and exit.",
    is_flag=True,
    default=Defaults.show_defaults,
    show_envvar=True,
    show_default=True,
)
OPT_ACTIVE = click.option(
    "--active / --inactive",
    "active",
    help="Set connection as active / inactive.",
    is_flag=True,
    default=True,
    show_envvar=True,
    show_default=True,
)
OPT_SAVE_AND_FETCH = click.option(
    "--save-and-fetch / --no-save-and-fetch",
    "-saf / -nsaf",
    "save_and_fetch",
    help="Fetch assets after saving.",
    is_flag=True,
    default=True,
    show_envvar=True,
    show_default=True,
)
OPT_EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
    help="Format of to export data in",
    default="table",
    show_envvar=True,
    show_default=True,
)
OPT_ID_CNX = click.option(
    "--id",
    "-i",
    "cnx_id",
    help="ID of connection",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_NODE_NAME = click.option(
    "--node-name",
    "-nn",
    "adapter_node",
    default=None,
    show_envvar=True,
    show_default=True,
    help="Node name (will default to core instance if not supplied)",
)
OPT_CNX_LABEL = click.option(
    "--connection-label",
    "-cl",
    "connection_label",
    default=None,
    show_envvar=True,
    show_default=True,
    help="Connection label to assign",
)

OPT_TUNNEL = click.option(
    "--tunnel",
    "-tn",
    "tunnel",
    default=None,
    show_envvar=True,
    show_default=True,
    help="Tunnel ID or Name",
)

OPT_ADAPTER_NAME = click.option(
    "--name",
    "-n",
    "adapter_name",
    required=True,
    show_envvar=True,
    show_default=True,
    help="Adapter name",
)
OPTS_PROMPTS = [
    OPT_PROMPT_FOR_OPTIONALS,
    OPT_PROMPT_FOR_DEFAULT,
    OPT_USE_SANE_DEFAULTS,
    OPT_IGNORE_UNKNOWNS,
]

OPTS_FLAGS = [
    OPT_ACTIVE,
    OPT_SAVE_AND_FETCH,
]
OPTS_SHOWS = [
    OPT_SHOW_SCHEMAS,
    OPT_SHOW_DEFAULTS,
]


OPTS_NODE = [
    OPT_TUNNEL,
    OPT_NODE_NAME,
    OPT_ADAPTER_NAME,
]
