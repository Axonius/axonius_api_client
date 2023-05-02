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

HELP: str = """
Local variables available:
    - axonapi: API client package itself
    - client/c: API Client connection object
    - ctx: Click context object
    - jdump/j: Helper function to pretty print python objects
    - j(HELP): this message

Local variables as shortcuts from client properties:
    - activity_logs/al: Work with activity logs
    - adapters/a: Work with adapters and adapter connections
    - dashboard/db: Work with discovery cycle
    - dashboard_spaces/dbs: Work with dashboard spaces
    - data_scopes/ds: Work with data scopes
    - devices/d: Work with device assets
    - folders/f: Work with folders
    - instances/i: Work with instances
    - meta/m: Work with instance metadata
    - remote_support/rs: Work with configuring system remote support
    - settings_global/sgl: Work with Global system settings
    - settings_gui/sgu: Work with GUI system settings
    - settings_lifecycle/sl: Work with lifecycle system settings
    - settings_ip/sip: Work with Identity Provider system settings
    - enforcements/e: Work with enforcements   
    - system_roles/sr: Work with system roles
    - system_users/su: Work with system users
    - users/u: Work with user assets
    - openapi/oas: Work with the OpenAPI specification file
    - vulnerabilities/v: Work with vulnerability assets
"""

SHELL_BANNER = f"Welcome human. We have some refreshments available for you:\n{HELP}"

SHELL_EXIT = """Goodbye human. We hope you enjoyed your stay."""

HISTPATH = os.path.expanduser("~")

HISTFILE = ".python_history"


def jdump(data):
    """Pass."""
    print(json_reload(data))


@click.command(name="shell", context_settings=CONTEXT_SETTINGS, epilog=f"\b\n\n{HELP}")
@add_options(AUTH)
@click.pass_context
def cmd(ctx, url, key, secret):  # noqa: D301
    f"""Start an interactive python shell with Axonius API Client loaded.

    The shell will authenticate to Axonius, setup autocompletion, enable history,
    and create the following objects:
    """
    client = ctx.obj.start_client(url=url, key=key, secret=secret, save_history=True)

    client.HTTP.save_history = True

    shellvars = {
        "activity_logs": client.activity_logs,
        "adapters": client.adapters,
        "axonapi": axonapi,
        "client": client,
        "ctx": ctx,
        "dashboard": client.dashboard,
        "dashboard_spaces": client.dashboard_spaces,
        "devices": client.devices,
        "data_scopes": client.data_scopes,
        "enforcements": client.enforcements,
        "folders": client.folders,
        "instances": client.instances,
        "jdump": jdump,
        "meta": client.meta,
        "openapi": client.openapi,
        "remote_support": client.remote_support,
        "settings_global": client.settings_global,
        "settings_gui": client.settings_gui,
        "settings_ip": client.settings_ip,
        "settings_lifecycle": client.settings_lifecycle,
        "system_roles": client.system_roles,
        "system_users": client.system_users,
        "users": client.users,
        "vulnerabilities": client.vulnerabilities,
        "a": client.adapters,
        "al": client.activity_logs,
        "c": client,
        "d": client.devices,
        "db": client.dashboard,
        "dbs": client.dashboard_spaces,
        "ds": client.data_scopes,
        "e": client.enforcements,
        "i": client.instances,
        "f": client.folders,
        "j": jdump,
        "m": client.meta,
        "oas": client.openapi,
        "rs": client.remote_support,
        "sgl": client.settings_global,
        "sgu": client.settings_gui,
        "sip": client.settings_ip,
        "sl": client.settings_lifecycle,
        "sr": client.system_roles,
        "su": client.system_users,
        "u": client.users,
        "v": client.vulnerabilities,
        "HELP": HELP,
    }

    spawn_shell(shellvars)


def write_hist_file():
    """Pass."""
    try:
        import readline

        hist_path = pathlib.Path(HISTPATH)
        hist_file = hist_path / HISTFILE

        hist_path.mkdir(mode=0o700, exist_ok=True)
        hist_file.touch(mode=0o600, exist_ok=True)

        readline.write_history_file(format(hist_file))
    except Exception as exc:  # pragma: no cover
        msg = f"Unable to import readline! {exc}"
        echo_error(msg, abort=False)


def register_readline(shellvars=None):
    """Pass."""
    shellvars = shellvars or {}

    hist_path = pathlib.Path(HISTPATH)
    hist_file = hist_path / HISTFILE

    hist_path.mkdir(mode=0o700, exist_ok=True)
    hist_file.touch(mode=0o600, exist_ok=True)

    try:
        try:
            import readline
        except ImportError:  # pragma: no cover
            # noinspection PyUnresolvedReferences
            import pyreadline as readline

        import rlcompleter

        readline.read_history_file(format(hist_file))
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

    if PY36:  # pragma: no cover
        args["exitmsg"] = SHELL_EXIT

    code.interact(**args)
