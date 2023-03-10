# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import datetime
import os
import typing as t

import click
import dotenv

from ...tools import get_path, json_dump

AX_ENV: str = str(get_path(os.environ.get("AX_ENV", "") or ".env"))


def multi_get(obj: dict, keys: t.List[str]) -> str:
    """Pass."""
    for key in keys:
        if obj.get(key):
            return obj[key]
    raise Exception(f"Unable to find any keys {keys} in dict {obj}")


def export_str(data: dict, url: str, signup: bool = False, **kwargs) -> str:
    """Pass."""
    ax_secret: str = multi_get(obj=data, keys=["ax_secret", "api_secret"])
    ax_key: str = multi_get(obj=data, keys=["ax_key", "api_key"])
    lines = [
        f'AX_URL="{url}"',
        f'AX_KEY="{ax_key}"',
        f'AX_SECRET="{ax_secret}"',
    ]
    if signup:
        lines.append(f'AX_BANNER="signup on {datetime.datetime.utcnow()}"')
    return "\n".join(lines)


def export_env(
    data: dict, url: str, signup: bool = False, env: t.Optional[str] = AX_ENV, **kwargs
) -> str:
    """Pass."""
    ax_secret: str = multi_get(obj=data, keys=["ax_secret", "api_secret"])
    ax_key: str = multi_get(obj=data, keys=["ax_key", "api_key"])

    env = get_path(env)
    if not env.is_file():
        click.secho(message=f"Creating file {str(env)!r}", err=True, fg="green")
        env.touch()
        env.chmod(0o600)
    else:
        click.secho(message=f"Updating file {str(env)!r}", err=True, fg="green")

    click.secho(
        message=f"Setting AX_URL, AX_KEY, and AX_SECRET in {str(env)!r}",
        err=True,
        fg="green",
    )
    dotenv.set_key(dotenv_path=str(env), key_to_set="AX_URL", value_to_set=url)
    dotenv.set_key(dotenv_path=str(env), key_to_set="AX_KEY", value_to_set=ax_key)
    dotenv.set_key(dotenv_path=str(env), key_to_set="AX_SECRET", value_to_set=ax_secret)
    return ""


def export_json(data: dict, url: str, **kwargs):
    """Pass."""
    data["url"] = url
    return json_dump(data)


EXPORT_FORMATS: dict = {
    "json": export_json,
    "str": export_str,
    "env": export_env,
}
