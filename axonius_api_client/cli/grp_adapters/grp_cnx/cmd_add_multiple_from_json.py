# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import textwrap

from ....exceptions import CnxAddError
from ....parsers.tables import tablize
from ....tools import coerce_bool, json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, INPUT_FILE, add_options, get_option_help

OPTIONS = [
    *AUTH,
    INPUT_FILE,
    get_option_help(choices=["multiple_cnx_json"]),
]


def wrap_value(value, width=30):
    """Pass."""
    if width is not None:
        return textwrap.fill(f"{value}", width=width)
    return value


@click.command(name="add-multiple-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file, **kwargs):
    """Add multiple connections from a JSON file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    data = ctx.obj.read_stream_json(stream=input_file, expect=list)

    if not data:
        ctx.obj.echo_error(msg=f"No connections provided!!! Data provided:\n{json_dump(data)}")

    keys = {
        "adapter": "Name of the adapter for the connection (REQUIRED, STRING)",
        "config": "Configuration of the connection (REQUIRED, DICTIONARY)",
        "node": "Name of the node running the adapter (OPTIONAL, STRING, DEFAULT: Core instance)",
        "save_and_fetch": "Save and fetch the connection (OPTIONAL, BOOLEAN, DEFAULT: True)",
        "active": "Set the connection as active (OPTIONAL, BOOLEAN, DEFAULT: True)",
    }
    keys_help = "\n - " + "\n - ".join([f"{k!r}: {v}" for k, v in keys.items()])
    keys_help = f"\nConnection keys help:{keys_help}"
    req_keys = ["adapter", "config"]
    added = []
    # TBD: split data validation of input file from adding cnx
    # validate adapter and node name (if supplied)
    # validate config TOO!!

    for idx, item in enumerate(data):
        try:
            if not isinstance(item, dict):
                raise Exception("Is not a dictionary")

            for key in req_keys:
                if key not in item:
                    raise Exception(f"Missing required key {key!r}{keys_help}")

            active = coerce_bool(item.get("active", True))
            save_and_fetch = coerce_bool(item.get("save_and_fetch", True))
            adapter = item.get("adapter")
            node = item.get("node", None)
            config = item.get("config", {})

            if not isinstance(config, dict):
                raise Exception("Configuration key is not a dictionary!")

            if not config:
                raise Exception("Empty configuration supplied!")

            with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
                try:
                    cnx_new = client.adapters.cnx.add(
                        adapter_name=adapter,
                        adapter_node=node,
                        save_and_fetch=save_and_fetch,
                        active=active,
                        **config,
                    )
                    ctx.obj.echo_ok(msg="Connection added successfully!")
                except CnxAddError as exc:
                    ctx.obj.echo_error(msg=f"{exc}", abort=False)
                    cnx_new = exc.cnx_new

                added.append(cnx_new)
        except Exception as exc:
            msg = [
                f"Connection #{idx + 1} had an error!",
                f"Connection:\n{json_dump(item)}",
                f"Error:\n{exc}",
            ]
            ctx.obj.echo_error(msg="\n\n".join(msg))

    out_keys = {
        "adapter_name": None,
        "node_name": None,
        "id": None,
        "uuid": None,
        "working": None,
        "error": 30,
    }
    out_added = [
        {k: wrap_value(v, out_keys.get(k)) for k, v in i.items() if k in out_keys} for i in added
    ]
    out_added_tbl = tablize(value=out_added, err="Connections added")
    ctx.obj.echo_ok(out_added_tbl)
