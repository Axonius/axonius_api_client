# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import constants, version
from . import cmd_shell, context, grp_adapters, grp_objects


# FUTURE: grp_enforcements
# FUTURE: wrap json datasets with objtype info
# FUTURE: --verbose/--no-verbose to silence echo_ok
# FUTURE: --warning/--no-warning to silence echo_warn
# FUTURE: way to only import cli stuffs so package doesnt see unless needed
# FUTURE: add cert_human logic
# FUTURE: prompt does not use CR when re-prompting on empty var with hide_input=False
# FUTURE: add doc links
@click.group()
@click.option(
    "--log-level-package",
    "-lpkg",
    default=constants.LOG_LEVEL_PACKAGE,
    help="Logging level to use for entire package.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-http",
    "-lhttp",
    default=constants.LOG_LEVEL_HTTP,
    help="Logging level to use for http client.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-auth",
    "-lauth",
    default=constants.LOG_LEVEL_AUTH,
    help="Logging level to use for auth client.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-api",
    "-lapi",
    default=constants.LOG_LEVEL_API,
    help="Logging level to use for api clients.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-console",
    "-lcon",
    default=constants.LOG_LEVEL_CONSOLE,
    help="Logging level to use for console output.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-level-file",
    "-lfile",
    default=constants.LOG_LEVEL_FILE,
    help="Logging level to use for file output.",
    type=click.Choice(constants.LOG_LEVELS_STR),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-console/--no-log-console",
    "-con/-ncon",
    default=False,
    help="Enable logging to --log-console-output.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file/--no-log-file",
    "-file/-nfile",
    default=False,
    help="Enable logging to --log-file-name in --log-file-path.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-request-attrs/--no-log-request-attrs",
    default=None,
    help="Log http client verbose or brief request attributes (none by default).",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-response-attrs/--no-log-response-attrs",
    default=None,
    help="Log http client verbose or brief response attributes (none by default).",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-request-body/--no-log-request-body",
    help="Log http client request body.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-response-body/--no-log-response-body",
    help="Log http client response body.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-name",
    "-file-name",
    default=constants.LOG_FILE_NAME,
    help="Send file logging to this file in --log-file-path.",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-path",
    "-file-path",
    default=constants.LOG_FILE_PATH,
    help="Send file logging to --log-file-name in this directory.",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-max-mb",
    "-file-mb",
    default=constants.LOG_FILE_MAX_MB,
    help="Rollover the log file when the size is this many MB.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--log-file-max-files",
    "-file-mf",
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
    "-cp",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to SSL certificate.",
    metavar="PATH",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--certverify/--no-certverify",
    "-cv/-ncv",
    default=False,
    help="Perform SSL Certificate Verification.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--certwarn/--no-certwarn",
    "-cw/-ncw",
    default=True,
    help="Show warning for self-signed SSL certificates.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--wraperror/--no-wraperror",
    "-we/-nwe",
    default=True,
    help="Show an error string instead of the full exception.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.version_option(version.__version__)
@context.pass_context
@click.pass_context
def cli(click_ctx, ctx, **kwargs):
    """Axonius API Client command line tool."""
    ctx._click_ctx = click_ctx
    ctx._connect_args.update(kwargs)
    context.load_dotenv()
    return ctx


cli.add_command(cmd_shell.cmd)
cli.add_command(grp_objects.devices)
cli.add_command(grp_objects.users)
cli.add_command(grp_adapters.adapters)
