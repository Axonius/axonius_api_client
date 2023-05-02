"""CLI for Cloudflare utilities."""
import click

from . import constants
from .flows import flow_get_token
from .tools import echoer


@click.command(
    # no_args_is_help=True,
    context_settings=constants.CLICK_CONTEXT,
)
@click.option(
    "--timeout-access",
    "-ta",
    "timeout_access",
    show_envvar=True,
    default=constants.TIMEOUT_ACCESS,
    type=click.INT,
    help="Timeout for `access token` command in seconds",
)
@click.option(
    "--timeout-login",
    "-tl",
    "timeout_login",
    show_envvar=True,
    default=constants.TIMEOUT_LOGIN,
    type=click.INT,
    help="Timeout for `access login` command in seconds",
)
@click.option(
    "--env/--no-env",
    "-env/-nenv",
    "env",
    is_flag=True,
    show_envvar=True,
    default=constants.FLOW_ENV,
    help=f"Try to get token from {constants.TOKEN_ENVS_STR}",
)
@click.option(
    "--run/--no-run",
    "-run/-nrun",
    "run",
    is_flag=True,
    show_envvar=True,
    default=constants.FLOW_RUN,
    help="If no token in OS env vars, try to get token from `access token` command",
)
@click.option(
    "--run-access/--no-run-access",
    "-runa/-nruna",
    "run_access",
    is_flag=True,
    show_envvar=True,
    default=constants.FLOW_RUN_ACCESS,
    help="If run is True , try to get token from `access token` command",
)
@click.option(
    "--run-login/--no-run-login",
    "-runl/-nrunl",
    "run_login",
    is_flag=True,
    show_envvar=True,
    default=constants.FLOW_RUN_LOGIN,
    help=(
        "If run is True and no token returned from `access token` command, "
        "try to get token from `access login` command (which should open a browser)"
    ),
)
@click.option(
    "--error/--no-error",
    "-err/-nerr",
    "error",
    is_flag=True,
    show_envvar=True,
    default=constants.FLOW_ERROR,
    help="Raise error if no token found",
)
@click.option(
    "--error-access/--no-error-access",
    "-erra/-nerra",
    "error_access",
    is_flag=True,
    show_envvar=True,
    default=constants.FLOW_ERROR,
    help="Raise error if `access token` command fails",
)
@click.option(
    "--error-login/--no-error-login",
    "-errl/-nerrl",
    "error_login",
    is_flag=True,
    show_envvar=True,
    default=constants.FLOW_ERROR,
    help="Raise error if `access login` command fails",
)
@click.option(
    "--echo/--no-echo",
    "-e/-ne",
    "echo",
    is_flag=True,
    show_envvar=True,
    default=constants.FLOW_ECHO,
    help="Echo commands and results to stderr",
)
@click.option(
    "--echo-verbose/--no-echo-verbose",
    "-ev/-nev",
    "echo_verbose",
    is_flag=True,
    show_envvar=True,
    default=constants.FLOW_ECHO_VERBOSE,
    help="Echo more stuff to stderr",
)
@click.option(
    "--log/--no-log",
    "-l/-nl",
    "logs",
    is_flag=True,
    show_envvar=True,
    default=constants.CLI_LOGS,
    help="Enable basic logging to stderr",
)
@click.option(
    "--path",
    "-p",
    "path",
    show_envvar=True,
    default=constants.CF_PATH,
    help=(
        "Path to cloudflared binary to run `access token` and `access login` commands."
        "can be full path or a binary in OS env var $PATH"
    ),
)
@click.option(
    "--url",
    "-u",
    "url",
    envvar=constants.URL_ENVS,
    show_envvar=True,
    default=None,
    help=(
        f"URL to use in `access token` and `access login` commands, will error if token not in "
        f"{constants.TOKEN_ENVS_STR} and url is not supplied or in {constants.URL_ENVS_STR}"
    ),
)
def get_token_cli(
    url: str,
    path: str = constants.CF_PATH,
    timeout_access: int = constants.TIMEOUT_ACCESS,
    timeout_login: int = constants.TIMEOUT_LOGIN,
    run: bool = constants.FLOW_RUN,
    run_login: bool = constants.FLOW_RUN_LOGIN,
    run_access: bool = constants.FLOW_RUN_ACCESS,
    env: bool = constants.FLOW_ENV,
    echo: bool = constants.FLOW_ECHO,
    echo_verbose: bool = constants.FLOW_ECHO_VERBOSE,
    error: bool = constants.FLOW_ERROR,
    error_access: bool = constants.FLOW_ERROR,
    error_login: bool = constants.FLOW_ERROR,
    logs: bool = constants.CLI_LOGS,
):
    """CLI to get cloudflare access token using cloudflared."""
    ctx = click.get_current_context()
    if logs:
        import logging
        import sys

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stderr,
        )

    try:
        token = flow_get_token(
            url=url,
            path=path,
            timeout_access=timeout_access,
            timeout_login=timeout_login,
            run=run,
            run_login=run_login,
            run_access=run_access,
            env=env,
            echo=echo,
            error=error,
            error_access=error_access,
            error_login=error_login,
            echo_verbose=echo_verbose,
        )
    except Exception as exc:
        echoer(f"{exc}", level="error", echo=True)
        ctx.exit(1)
    else:
        echoer(f"Token for {url}", log=False, echo=echo)
        print(token)
        ctx.exit(0)
