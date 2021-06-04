# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import datetime
import time

import click

from ...api import Signup
from ...tools import dt_now
from ..context import CONTEXT_SETTINGS
from ..options import URL, add_options

OPTIONS = [
    URL,
    click.option(
        "--wait/--no-wait",
        "-w/-nw",
        "wait",
        help="Wait until system is ready before returning",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sleep",
        "sleep",
        help="Seconds to wait for each ready check",
        type=click.IntRange(min=0),
        default=30,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--max-wait",
        "max_wait",
        help="Maximum seconds to wait",
        type=click.IntRange(min=1),
        default=60 * 15,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="system-status", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, wait, sleep, max_wait):
    """Get the status of the Axonius instance."""

    def get_status():
        """Get the system status safely."""
        try:
            data = entry.system_status
            message = data.msg
            status_code = data.status_code
            is_ready = data.is_ready
        except Exception as exc:
            message = f"HTTP Error: {exc}"
            status_code = 1000
            is_ready = False

        msg = [
            f"URL: {entry.http.url}",
            f"Date: {dt_now()}",
            f"Message: {message}",
            f"Status Code: {status_code}",
            f"Ready: {is_ready}",
        ]
        click.secho("\n".join(msg))
        return is_ready, status_code

    entry = Signup(url=url)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        is_ready, status_code = get_status()

    if wait:
        max_wait_dt = dt_now() + datetime.timedelta(seconds=max_wait)
        while not is_ready:
            click.secho("-" * 50)
            is_ready, status_code = get_status()
            if dt_now() >= max_wait_dt:
                click.secho(f"Stopping, hit max_wait of {max_wait_dt}")
                break
            time.sleep(sleep)

    ctx.exit(status_code)
