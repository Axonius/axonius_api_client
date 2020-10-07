# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import atexit
import os

import click

import axonius_api_client as axonapi

from ...constants.general import PY36
from ...tools import echo_error, json_reload, pathlib
from ..context import CONTEXT_SETTINGS
from ..options import AUTH, add_options

SHELL_BANNER = """Welcome human. We have some refreshments available for you:

    - ctx: Click context object
    - client/c: API Client connection object
    - jdump/j: Helper function to pretty print python objects
    - axonapi: API client package itself

API Objects:
    - devices/d: Work with device assets
    - users/u: Work with user assets
    - adapters/a: Work with adapters and adapter connections
    - dashboard/db: Work with dashboards and discovery cycle
    - instances/i: Work with instances
    - system_users/su: Work with system users
    - system_roles/sr: Work with system roles
    - meta/m: Work with instance metadata
    - settings_global/sgl: Work with Global system settings
    - settings_gui/sgu: Work with GUI system settings
    - settings_lifecycle/sl: Work with Lifecyle system settings
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
        - axonapi: API Client package itself
        - client/c: API Client connection object
        - devices/d: Work with device assets
        - users/u: Work with user assets
        - adapters/a: Work with adapters and adapter connections
        - system/s: Work with users, roles, global settings, and more
        - dashboard/db: Work with dashboards and discovery cycle
        - instances/i: Work with instances
        - system_users/su: Work with system users
        - system_roles/sr: Work with system roles
        - meta/m: Work with instance metadata
        - settings_global/sgl: Work with Global system settings
        - settings_gui/sgu: Work with GUI system settings
        - settings_lifecycle/sl: Work with Lifecyle system settings
        - jdump/j: Helper function to pretty print python objects

    """
    client = ctx.obj.start_client(url=url, key=key, secret=secret, save_history=True)

    client.HTTP.save_history = True

    shellvars = {
        "adapters": client.adapters,
        "axonapi": axonapi,
        "client": client,
        "ctx": ctx,
        "dashboard": client.dashboard,
        "devices": client.devices,
        "enforcements": client.enforcements,
        "instances": client.instances,
        "jdump": jdump,
        "users": client.users,
        "system_users": client.system_users,
        "system_roles": client.system_roles,
        "meta": client.meta,
        "settings_global": client.settings_global,
        "settings_gui": client.settings_gui,
        "settings_lifecycle": client.settings_lifecycle,
        "a": client.adapters,
        "c": client,
        "d": client.devices,
        "db": client.dashboard,
        "e": client.enforcements,
        "i": client.instances,
        "j": jdump,
        "u": client.users,
        "su": client.system_users,
        "sr": client.system_roles,
        "m": client.meta,
        "sgl": client.settings_global,
        "sgu": client.settings_gui,
        "sl": client.settings_lifecycle,
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
