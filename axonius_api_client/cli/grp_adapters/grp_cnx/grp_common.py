# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....api.parsers.tables import tablize_cnxs, tablize_schemas
from ....constants import CNX_SANE_DEFAULTS
from ....tools import json_dump, listify, pathlib
from ...context import click

PATH_PROMPT = click.Path(
    exists=True,
    file_okay=True,
    dir_okay=False,
    writable=False,
    readable=True,
    resolve_path=True,
    allow_dash=False,
    path_type=None,
)

HIDDEN = ["secret", "key", "password"]

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(
        ["json-full", "json-config", "json", "table", "table-schemas", "str", "str-args"]
    ),
    help="Format of to export data in",
    default="json-config",
    show_envvar=True,
    show_default=True,
)


def prompt_schema(schema, config, prompt_optional, prompt_default, adapter_name):
    """Pass."""
    name = schema["name"]
    required = schema["required"]
    stype = schema["type"]
    default = schema.get("default", None)
    fmt = schema.get("format", "")
    enum = schema.get("enum", [])

    if enum:
        str_type = click.Choice(choices=enum, case_sensitive=True)
    else:
        str_type = None

    schema["hide_input"] = hide_input = fmt == "password" or name in HIDDEN

    if name in config:
        return

    sane_defaults = CNX_SANE_DEFAULTS.get(adapter_name, CNX_SANE_DEFAULTS["all"])
    if name in sane_defaults and default is None:
        default = sane_defaults[name]

    if not prompt_default and default is not None:
        config[name] = default
        return

    if not required:
        if not prompt_optional:
            return

        show_schema(schema=schema)

        do_prompt = click.prompt(
            text="Prompt for this optional item?",
            default=True,
            type=click.BOOL,
            err=True,
            show_default=True,
        )

        if not do_prompt:
            return
    else:
        show_schema(schema=schema)

    if stype == "file":
        value = click.prompt(text="Enter value", type=PATH_PROMPT, err=True)
        value = pathlib.Path(value).expanduser().resolve()

    if stype == "bool":
        value = click.prompt(
            text="Enter value",
            default=default,
            type=click.BOOL,
            err=True,
            show_default=True,
            show_choices=True,
        )

    if stype in ["number", "integer"]:
        value = click.prompt(
            text="Enter value",
            default=default,
            type=click.INT,
            err=True,
            show_default=True,
            show_choices=True,
        )

    if stype == "array":
        value = click.prompt(
            text="Enter value",
            default=default,
            err=True,
            type=str_type,
            hide_input=hide_input,
            show_default=True,
            show_choices=True,
        )
        value = [x.strip() for x in value.strip().split(",") if x.strip()]

    if stype == "string":
        value = click.prompt(
            text="Enter value",
            default=default,
            err=True,
            type=str_type,
            hide_input=hide_input,
            show_default=True,
            show_choices=True,
        )

    config[name] = value


def show_schema(schema, err=True):
    """Pass."""
    rkw = ["{}: {}".format(k, v) for k, v in schema.items()]
    rkw = "\n  " + "\n  ".join(rkw)
    click.secho(message=f"\n***  Configuration schema:{rkw}", fg="blue", err=err)


def handle_export(ctx, rows, export_format):
    """Pass."""
    if export_format == "json":
        if isinstance(rows, list):
            for row in rows:
                row.pop("schemas")
        else:
            rows.pop("schemas")
        click.secho(json_dump(rows))
        ctx.exit(0)

    if export_format == "json-config":
        if isinstance(rows, list):
            rows = [x["config"] for x in rows]
        else:
            rows = rows["config"]
        click.secho(json_dump(rows))
        ctx.exit(0)

    if export_format == "json-full":
        click.secho(json_dump(rows))
        ctx.exit(0)

    if export_format == "table":
        rows = listify(rows)
        click.secho(tablize_cnxs(cnxs=rows))
        ctx.exit(0)

    if export_format == "table-schemas":
        if isinstance(rows, list):
            schemas = rows[0]["schemas"]
        else:
            schemas = rows["schemas"]
        click.secho(
            tablize_schemas(
                schemas=schemas,
                err=None,
                fmt="simple",
                footer=True,
                orig=True,
                orig_width=20,
            )
        )
        ctx.exit(0)

    if export_format == "str-args":
        rows = listify(rows)
        lines = "\n".join(
            [
                "--node-name {node_name} --name {adapter_name} --id {id}".format(**row)
                for row in rows
            ]
        )
        click.secho(lines)
        ctx.exit(0)

    if export_format == "str":
        rows = listify(rows)
        lines = "\n".join(["{id}".format(**row) for row in rows])
        click.secho(lines)
        ctx.exit(0)

    ctx.exit(1)


# def get_handler(ctx, url, key, secret, export_format, **kwargs):
#     """Pass."""
#     client = ctx.obj.start_client(url=url, key=key, secret=secret)

#     with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
#         rows = client.adapters.cnx.get_by_adapter(**kwargs)
#     handle_export(ctx=ctx, rows=rows, export_format=export_format)


# def get_by_id_handler(ctx, url, key, secret, export_format, **kwargs):
#     """Pass."""
#     client = ctx.obj.start_client(url=url, key=key, secret=secret)

#     with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
#         rows = client.adapters.cnx.get_by_id(**kwargs)
#     handle_export(ctx=ctx, rows=rows, export_format=export_format)

# def add_handler(
#     ctx,
#     url,
#     key,
#     secret,
#     config,
#     export_format,
#     prompt_optional,
#     prompt_default,
#     adapter_name,
#     adapter_node,
#     **kwargs,
# ):  # noqa
#     """Pass."""

#     client = ctx.obj.start_client(url=url, key=key, secret=secret)

#     config = dict(config)
#     kwargs["kwargs_config"] = config

#     with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
#         adapter = client.adapters.get_by_name(name=adapter_name, node=adapter_node)

#     schemas = list(adapter["schemas"]["cnx"].values())
#     schemas = reversed(sorted(schemas, key=lambda x: [x["required"], x["name"]]))

#     for schema in schemas:
#         prompt_schema(
#             schema=schema,
#             config=config,
#             prompt_optional=prompt_optional,
#             prompt_default=prompt_default,
#             adapter_name=adapter_name,
#         )

#     with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
#         try:
#             cnx_new = client.adapters.cnx.add(
#                 adapter_name=adapter_name, adapter_node=adapter_node, **config
#             )
#             ctx.obj.echo_ok(msg=f"Connection added successfully!")

#         except CnxAddError as exc:
#             ctx.obj.echo_error(msg=f"{exc}", abort=False)
#             cnx_new = exc.cnx_new

#     handle_export(ctx=ctx, rows=cnx_new, export_format=export_format)
# from ....exceptions import CnxAddError


# # -*- coding: utf-8 -*-
# """Command line interface for Axonius API Client."""
# from ...context import click
# from ...options import AUTH, NODE_CNX, SPLIT_CONFIG_OPT  # , CONTENTS,

# GET = [
#     *AUTH,
#     EXPORT,
#     *NODE_CNX,
# ]

# GET_BY_ID = [
#     *GET,
#     click.option(
#         "--id",
#         "-i",
#         "cnx_id",
#         help="ID of connection",
#         required=True,
#         show_envvar=True,
#         show_default=True,
#     ),
# ]
# from ...options import AUTH, NODE_CNX, SPLIT_CONFIG_OPT  # , CONTENTS,
