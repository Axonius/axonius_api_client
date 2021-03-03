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

    - axonapi: API client package itself
    - client/c: API Client connection object
    - ctx: Click context object
    - jdump/j: Helper function to pretty print python objects

API Objects:
    - activity_logs/al: Work with activity logs
    - adapters/a: Work with adapters and adapter connections
    - dashboard/db: Work with dashboards and discovery cycle
    - devices/d: Work with device assets
    - instances/i: Work with instances
    - meta/m: Work with instance metadata
    - remote_support/rs: Work with configuring system remote support
    - settings_global/sgl: Work with Global system settings
    - settings_gui/sgu: Work with GUI system settings
    - settings_lifecycle/sl: Work with Lifecyle system settings
    - settings_ip/sip: Work with Identity Provider system settings
    - system_roles/sr: Work with system roles
    - system_users/su: Work with system users
    - users/u: Work with user assets

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
        - axonapi: API Client package itself
        - client/c: API Client connection object
        - ctx: Click context object
        - jdump/j: Helper function to pretty print python objects

        - activity_logs/al: Work with activity logs
        - adapters/a: Work with adapters and adapter connections
        - dashboard/db: Work with dashboards and discovery cycle
        - devices/d: Work with device assets
        - instances/i: Work with instances
        - meta/m: Work with instance metadata
        - remote_support/rs: Work with configuring system remote support
        - settings_global/sgl: Work with Global system settings
        - settings_gui/sgu: Work with GUI system settings
        - settings_lifecycle/sl: Work with Lifecyle system settings
        - settings_ip/sip: Work with Identity Provider system settings
        - system_roles/sr: Work with system roles
        - system_users/su: Work with system users
        - users/u: Work with user assets

    """
    client = ctx.obj.start_client(url=url, key=key, secret=secret, save_history=True)

    client.HTTP.save_history = True

    shellvars = {
        "adapters": client.adapters,
        "activity_logs": client.activity_logs,
        "axonapi": axonapi,
        "client": client,
        "ctx": ctx,
        "dashboard": client.dashboard,
        "devices": client.devices,
        "enforcements": client.enforcements,
        "instances": client.instances,
        "jdump": jdump,
        "users": client.users,
        "remote_support": client.remote_support,
        "system_users": client.system_users,
        "system_roles": client.system_roles,
        "meta": client.meta,
        "settings_global": client.settings_global,
        "settings_gui": client.settings_gui,
        "settings_lifecycle": client.settings_lifecycle,
        "settings_ip": client.settings_ip,
        "a": client.adapters,
        "al": client.activity_logs,
        "c": client,
        "d": client.devices,
        "db": client.dashboard,
        "e": client.enforcements,
        "i": client.instances,
        "j": jdump,
        "u": client.users,
        "su": client.system_users,
        "sr": client.system_roles,
        "rs": client.remote_support,
        "m": client.meta,
        "sgl": client.settings_global,
        "sgu": client.settings_gui,
        "sl": client.settings_lifecycle,
        "sip": client.settings_ip,
    }

    spawn_shell(shellvars)


def write_hist_file():
    """Pass."""
    try:
        import readline

        histpath = pathlib.Path(HISTPATH)
        histfile = histpath / HISTFILE

        histpath.mkdir(mode=0o700, exist_ok=True)
        histfile.touch(mode=0o600, exist_ok=True)

        readline.write_history_file(format(histfile))
    except Exception as exc:
        msg = f"Unable to import readline! {exc}"
        echo_error(msg, abort=False)


def register_readline(shellvars=None):
    """Pass."""
    shellvars = shellvars or {}

    histpath = pathlib.Path(HISTPATH)
    histfile = histpath / HISTFILE

    histpath.mkdir(mode=0o700, exist_ok=True)
    histfile.touch(mode=0o600, exist_ok=True)

    try:
        try:
            import readline
        except Exception:  # pragma: no cover
            import pyreadline as readline

        import rlcompleter

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
    register_readline(shellvars=shellvars)

    args = {"local": shellvars, "banner": SHELL_BANNER}

    if PY36:
        args["exitmsg"] = SHELL_EXIT

    code.interact(**args)
