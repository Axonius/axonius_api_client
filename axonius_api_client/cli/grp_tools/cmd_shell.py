# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import atexit
import os

import click

import axonius_api_client as axonapi

from ...constants import PY36
from ...tools import echo_error, json_reload, pathlib
from ..context import CONTEXT_SETTINGS
from ..options import AUTH, add_options

SHELL_BANNER = """Welcome human. We have some refreshments available for you:

    - ctx: Click context object
    - client/c: Instance of axonius_api_client.connect.Connect
    - jdump/j: Helper function to pretty print python objects
    - axonapi: API client package itself

API Objects:
    - adapters/a: Instance of axonius_api_client.api.Adapters
    - devices/d: Instance of axonius_api_client.api.Devices
    - users/u: Instance of axonius_api_client.api.Users
    - system/s: Instance of axonius_api_client.api.System
    - enforcements/e: Instance of axonius_api_client.api.Enforcements
"""

SHELL_EXIT = """Goodbye human. We hope you enjoyed your stay."""

HISTPATH = os.path.expanduser("~")

HISTFILE = ".python_history"


def jdump(data):
    """Pass."""
    print(json_reload(data))


@click.command(name="shell", context_settings=CONTEXT_SETTINGS)
@add_options(AUTH)
@click.pass_context
def cmd(ctx, url, key, secret):  # noqa: D301
    """Start an interactive python shell.

    The shell will authenticate to Axonius, setup autocompletion, enable history,
    and create the following objects:

    \b
        - ctx: Click context object
        - client/c: Instance of axonius_api_client.connect.Connect
        - devices/d: Instance of axonius_api_client.api.Devices
        - users/u: Instance of axonius_api_client.api.Users
        - adapters/a: Instance of axonius_api_client.api.Adapters
        - system/s: Instance of axonius_api_client.api.System
        - axonapi: API Client package itself
        - jdump/j: Helper function to pretty print python objects

    """
    client = ctx.obj.start_client(url=url, key=key, secret=secret, save_history=True)

    client._http.save_history = True

    shellvars = {
        "ctx": ctx,
        "client": client,
        "c": client,
        "devices": client.devices,
        "d": client.devices,
        "users": client.users,
        "u": client.users,
        "adapters": client.adapters,
        "a": client.adapters,
        "jdump": jdump,
        "j": jdump,
        "enforcements": client.enforcements,
        "e": client.enforcements,
        "s": client.system,
        "system": client.system,
        "axonapi": axonapi,
    }

    spawn_shell(shellvars)


def write_hist_file():
    """Pass."""
    import readline

    histpath = pathlib.Path(HISTPATH)
    histfile = histpath / HISTFILE

    histpath.mkdir(mode=0o700, exist_ok=True)
    histfile.touch(mode=0o600, exist_ok=True)

    readline.write_history_file(format(histfile))


def register_readline(shellvars=None):
    """Pass."""
    try:
        import readline
    except Exception:  # pragma: no cover
        import pyreadline as readline

    import rlcompleter

    shellvars = shellvars or {}

    histpath = pathlib.Path(HISTPATH)
    histfile = histpath / HISTFILE

    histpath.mkdir(mode=0o700, exist_ok=True)
    histfile.touch(mode=0o600, exist_ok=True)

    try:
        readline.read_history_file(format(histfile))
        atexit.register(write_hist_file)

        readline.set_completer(rlcompleter.Completer(shellvars).complete)

        readline_doc = getattr(readline, "__doc__", "")
        is_libedit = readline_doc and "libedit" in readline_doc

        pab = "bind ^I rl_complete" if is_libedit else "tab: complete"
        readline.parse_and_bind(pab)
    except Exception as exc:
        msg = "Unable to register history and autocomplete:\n{}".format(exc)
        echo_error(msg, abort=False)


def spawn_shell(shellvars=None):
    """Pass."""
    import code

    shellvars = shellvars or {}
    register_readline(shellvars)

    args = {"local": shellvars, "banner": SHELL_BANNER}

    if PY36:
        args["exitmsg"] = SHELL_EXIT

    code.interact(**args)
