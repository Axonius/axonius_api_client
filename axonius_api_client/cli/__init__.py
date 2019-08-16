# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import click

from . import context, cmd_object_fields, cmd_adapters, cmd_shell
from .. import tools, constants, version, logs

AX_DOTENV = os.environ.get("AX_DOTENV", "")
CWD_PATH = tools.resolve_path(os.getcwd())


# FUTURE: prompt does not use CR when re-prompting on empty var with hide_input=False
# FUTURE: add doc links
@click.group()
@click.option(
    "--log-level-package",
    default=constants.LOG_LEVEL_PACKAGE,
    help="Logging level to use for entire package.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-http",
    default=constants.LOG_LEVEL_HTTP,
    help="Logging level to use for http client.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-auth",
    default=constants.LOG_LEVEL_AUTH,
    help="Logging level to use for auth client.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-api",
    default=constants.LOG_LEVEL_API,
    help="Logging level to use for api clients.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-console",
    default=constants.LOG_LEVEL_CONSOLE,
    help="Logging level to use for console output.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-file",
    default=constants.LOG_LEVEL_FILE,
    help="Logging level to use for file output.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-override",
    help="Override the logging level for everything.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-console/--no-log-console",
    default=False,
    help="Enable logging to --log-console-output.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-console-output",
    default="stderr",
    help="Send console logging to stderr or stdout.",
    type=click.Choice(["stderr", "stdout"]),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file/--no-log-file",
    default=False,
    help="Enable logging to --log-file-name in --log-file-path.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-name",
    default=constants.LOG_FILE_NAME,
    help="Send file logging to this file in --log-file-path.",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-path",
    default=constants.LOG_FILE_PATH,
    help="Send file logging to --log-file-name in this directory.",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-max-mb",
    default=constants.LOG_FILE_MAX_MB,
    help="Rollover the log file when the size is this many MB.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-max-files",
    default=constants.LOG_FILE_MAX_FILES,
    help="Only keep this many rollover logs.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--proxy",
    default="",
    help="Proxy to use to connect to Axonius instance.",
    metavar="PROXY",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--certpath",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to SSL certificate.",
    metavar="PATH",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--certverify/--no-certverify",
    default=False,
    help="Perform SSL Certificate Verification.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--certwarn/--no-certwarn",
    default=True,
    help="Show warning for self-signed SSL certificates.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--wraperror/--no-wraperror",
    default=True,
    help="Show an error string instead of the full exception.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.version_option(version.__version__)
@context.pass_context
def cli(ctx, log_level_override, **kwargs):
    """Axonius API Client command line tool."""
    log_console_output = kwargs.get("log_console_output", "stderr")

    if log_console_output == "stderr":
        kwargs["log_console_method"] = logs.add_stderr
    elif log_console_output == "stdout":
        kwargs["log_console_method"] = logs.add_stdout

    if log_level_override:
        for k, v in kwargs.items():
            if "log_level_" not in k:
                continue
            kwargs[k] = log_level_override

    ctx._connect_args.update(kwargs)
    return ctx


@cli.group()
@context.pass_context
def devices(ctx):
    """Work with device objects."""
    return ctx


@cli.group()
@context.pass_context
def users(ctx):
    """Work with user objects."""
    return ctx


@cli.group()
@context.pass_context
def adapters(ctx):
    """Work with adapter objects."""
    return ctx


cli.add_command(cmd_shell.shell)
devices.add_command(cmd_object_fields.cmd)
users.add_command(cmd_object_fields.cmd)
adapters.add_command(cmd_adapters.clients)


def main(*args, **kwargs):
    """Pass."""
    context.load_dotenv()
    return cli(*args, **kwargs)


if __name__ == "__main__":
    main()

# report of all adapters missing from all devices
# report of all adapters missing from all users

# adapters field missing any clients configured for any adapters?
# fetch time field? older than N days?

# report of broken adapter clients
