# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import atexit

import click

from ... import tools
from .. import cli_constants, context, options


def jdump(data):
    """Pass."""
    print(tools.json_reload(data))


@click.command(name="shell", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
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
    }

    spawn_shell(shellvars)


def write_hist_file():
    """Pass."""
    import readline

    histpath = tools.pathlib.Path(cli_constants.HISTPATH)
    histfile = histpath / cli_constants.HISTFILE

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

    histpath = tools.pathlib.Path(cli_constants.HISTPATH)
    histfile = histpath / cli_constants.HISTFILE

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
        context.Context.echo_error(msg, abort=False)


def spawn_shell(shellvars=None):
    """Pass."""
    import code

    shellvars = shellvars or {}
    register_readline(shellvars)

    args = {"local": shellvars, "banner": cli_constants.SHELL_BANNER}

    if tools.six.PY3:
        args["exitmsg"] = cli_constants.SHELL_EXIT

    code.interact(**args)
