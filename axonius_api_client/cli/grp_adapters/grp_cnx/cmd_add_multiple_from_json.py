# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxAddError
from ....tools import coerce_bool, json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import ABORT, AUTH, INPUT_FILE, add_options, get_option_help
from .grp_common import EXPORT_FORMATS, OPT_EXPORT, OPT_IGNORE_UNKNOWNS, OPT_USE_SANE_DEFAULTS
from .parsing import parse_config

OPTIONS = [
    *AUTH,
    OPT_USE_SANE_DEFAULTS,
    OPT_IGNORE_UNKNOWNS,
    ABORT,
    INPUT_FILE,
    OPT_EXPORT,
    get_option_help(choices=["multiple_cnx_json"]),
]


KEYS = {
    "adapter_name": "Adapter name to add connection to (REQUIRED, STRING)",
    "config": "Configuration of the connection (REQUIRED, DICTIONARY)",
    "node_name": "Node name to add connection to (OPTIONAL, STRING, DEFAULT: Core instance)",
    "tunnel": "Tunnel to add connection to (OPTIONAL, STRING, DEFAULT: None)",
    "save_and_fetch": "Save and fetch or just save (OPTIONAL, BOOLEAN, DEFAULT: True)",
    "active": "Set as active or inactive (OPTIONAL, BOOLEAN, DEFAULT: True)",
}
KEYS_HELP = "\n - " + "\n - ".join([f"{k!r}: {v}" for k, v in KEYS.items()])
KEYS_HELP = f"Connection keys help:{KEYS_HELP}"
REQ_KEYS = ["adapter_name", "config"]


def parse_item(item):
    """Pass."""

    def trybool(key, default=True):
        value = item.get(key, default)
        try:
            return coerce_bool(value)
        except Exception as exc:
            errs.append(f"{key!r} is not a valid bool: {exc}")

    def fixit(oldkey, newkey):
        if oldkey in item:
            item[newkey] = item.pop(oldkey)

    def check_type(key, ctype, default=None):
        value = item.get(key, default)
        if not isinstance(value, ctype) or not value:
            errs.append(
                f"{key!r} with value {value!r} type {type(value)} is not a {ctype} or is empty"
            )
        return value

    fixit("adapter", "adapter_name")
    fixit("node", "node_name")

    errs = []
    errs += [f"{x!r} key is required but was not supplied" for x in REQ_KEYS if x not in item]

    parsed = {}
    parsed["active"] = trybool(key="active")
    parsed["save_and_fetch"] = trybool(key="save_and_fetch")
    parsed["adapter_name"] = check_type(key="adapter_name", ctype=str)
    parsed["adapter_node"] = item.get("adapter_node", None)
    parsed["new_config"] = check_type(key="config", ctype=dict)
    parsed["tunnel"] = item.get("tunnel", None)

    if errs:
        raise Exception("\n".join(errs))

    return parsed


@click.command(name="add-multiple-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    input_file,
    abort,
    export_format,
    use_sane_defaults,
    ignore_unknowns,
    help_detailed,
):
    """Add multiple connections from a JSON file."""

    def do_item(item, idx):
        def echo_err(msg):
            ctx.obj.error_count += 1
            ctx.obj.echo_error(msg=msg, abort=abort)

        def stop(msg):
            echo_err(f"{info} Stopped processing! {msg}")

        info = f"Connection item #{idx + 1}/{len(items)}"
        ctx.obj.echo_ok(f"{info} Now processing\n")

        try:
            parsed = parse_item(item=item)
        except Exception as exc:
            msg = [
                f"supplied:\n{json_dump(item)}",
                KEYS_HELP,
                f"{info} initial parsing errors:\n{exc}",
            ]
            stop("\n\n".join(msg))
            return

        try:
            adapter = client.adapters.get_by_name(
                name=parsed["adapter_name"], node=parsed["adapter_node"]
            )
            cnxs = client.adapters.cnx._get(adapter_name=adapter["name_raw"])
        except Exception as exc:
            stop(f"Error while getting adapter and connection schemas:\n{exc}")
            return

        parsed["adapter_name"] = adapter["name"]
        parsed["adapter_node"] = adapter["node_name"]
        schemas = list(cnxs.schema_cnx.values())

        try:
            parsed["new_config"] = parse_config(
                schemas=schemas,
                adapter_name=adapter["name"],
                config=parsed["new_config"],
                use_sane_defaults=use_sane_defaults,
                prompt_for_optional=False,
                prompt_for_default=False,
                prompt_for_missing_required=False,
                ignore_unknowns=ignore_unknowns,
                error_as_exc=True,
            )
        except Exception as exc:
            stop(f"Error while parsing supplied config:\n{exc}")
            return

        with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror, abort=abort):
            try:
                data = client.adapters.cnx.add(**parsed)
                ctx.obj.echo_ok(msg=f"{info} Connection added with no errors")
                return data
            except CnxAddError as exc:
                if not ctx.obj.wraperror and abort:  # pragma: no cover
                    raise

                echo_err(msg=f"{info} Connection added with error: {exc}")
                return exc.cnx_new

    ctx.obj.error_count = 0
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    items = ctx.obj.read_stream_json(stream=input_file, expect=list, expect_items=dict, items_min=1)
    ctx.obj.echo_ok(f"Begin processing of {len(items)} items")

    data = [do_item(item=x, idx=idx) for idx, x in enumerate(items)]
    data = [x for x in data if x]
    ctx.obj.echo_ok(
        f"Added {len(data)} out of {len(items)} connections (error count: {ctx.obj.error_count})"
    )
    if data:
        click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(100 if ctx.obj.error_count else 0)
