# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import datetime
import time

import click

from ...setup_env import convert_key, write_dotenv
from ...tools import dt_now, json_dump


def handle_keys(
    ctx,
    data: dict,
    config: dict,
    url: str,
    write_env: bool,
    env_file: str,
    export_format: str = "str",
):
    """Pass."""
    api_key = data["api_key"]
    api_secret = data["api_secret"]
    config = {convert_key(k): v for k, v in dict(config).items()}

    values = {
        convert_key("URL"): url,
        convert_key("KEY"): api_key,
        convert_key("SECRET"): api_secret,
    }
    values.update(config)

    if write_env:
        wrote = {}
        for k, v in values.items():
            env_file, used_key, used_value = write_dotenv(ax_env=env_file, key=k, value=v)
            wrote[used_key] = used_value
        ctx.obj.echo_ok(f"Wrote keys {list(wrote)} to: {str(env_file)!r}")
    else:
        if export_format == "str":
            for k, v in values.items():
                click.secho(f'{k}="{v}"')
        elif export_format == "json":
            data["url"] = url
            click.secho(json_dump(data))


def get_status(ctx, client, wrap=False):
    """Get the system status safely."""
    try:
        data = client.signup.system_status
        message = data.msg
        status_code = data.status_code
        is_ready = data.is_ready
    except Exception as exc:
        if not wrap:
            raise
        message = f"HTTP Error: {exc}"
        status_code = 1000
        is_ready = False

    msg = [
        f"URL: {client.HTTP.url}",
        f"Date: {dt_now()}",
        f"Message: {message}",
        f"Status Code: {status_code}",
        f"Ready: {is_ready}",
    ]
    click.secho("\n".join(msg))
    return is_ready, status_code


def do_wait_status(ctx, client, max_wait=60 * 15, sleep=30, is_ready=False):
    """Pass."""
    max_wait_dt = dt_now() + datetime.timedelta(seconds=max_wait)
    while not is_ready:
        click.secho("-" * 50)
        is_ready, status_code = get_status(ctx=ctx, client=client)
        if dt_now() >= max_wait_dt:
            click.secho(f"Stopping, hit max_wait of {max_wait_dt}")
            break
        time.sleep(sleep)
