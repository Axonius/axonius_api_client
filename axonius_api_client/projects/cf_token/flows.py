"""Workflows for getting an access token for accessing a website behind cloudflare."""
import functools
import pathlib
import subprocess
import typing as t

from .tools import (
    echoer,
    check_is_token,
    get_env_token,
    listify,
    get_cmd_stderr,
    find_cloudflared,
    check_is_url,
    get_env_url,
    run_command,
    check_result_is_token,
    args_str,
    join_it,
)

from . import constants


class GetTokenError(ValueError):
    """Generic error for get_token flows."""

    def __init__(
        self,
        message: t.Optional[t.Union[str, t.Iterable[str]]] = None,
        helps: t.Optional[t.Union[str, t.Iterable[str]]] = None,
        exception: t.Optional[Exception] = None,
        add_helps: bool = True,
        add_exception: bool = True,
        add_source: bool = True,
        source: t.Optional[str] = None,
    ) -> None:
        """Constructor.

        Args:
            message: message to show
            exception: exception that caused this error
            add_helps: add help messages
            add_exception: add exception info
            add_source: add source info
            helps: help messages to show
            source: source info to show
        """
        msgs: t.List[str] = listify(message)
        helps: t.List[str] = listify(helps)

        if add_source and source:
            msgs += ["", f"While in {source}"]

        if add_exception and exception:
            msgs += ["", f"Exception type {type(exception)} message {exception}"]

        if add_helps:
            helps_str = "\n - " + "\n - ".join(helps) if helps else ""
            msgs += ["", f"Try the following:{helps_str}", ""] if helps else []

        self.msg = "\n".join(msgs)
        self.exception = exception
        self.source = source
        super().__init__(self.msg)


def flow_get_token(
    url: t.Optional[str] = None,
    token: t.Optional[str] = None,
    env: bool = constants.FLOW_ENV,
    run: bool = constants.FLOW_RUN,
    run_access: bool = constants.FLOW_RUN_ACCESS,
    run_login: bool = constants.FLOW_RUN_LOGIN,
    path: constants.PathLike = constants.CF_PATH,
    timeout_access: t.Optional[int] = constants.TIMEOUT_ACCESS,
    timeout_login: t.Optional[int] = constants.TIMEOUT_LOGIN,
    error: bool = constants.FLOW_ERROR,
    error_access: bool = constants.FLOW_ERROR,
    error_login: bool = constants.FLOW_ERROR,
    echo: bool = constants.FLOW_ECHO,
    echo_verbose: bool = constants.FLOW_ECHO_VERBOSE,
) -> t.Optional[str]:
    """Get cf-access-token from supplied token, environment variables, or cloudflared binary.

    Notes:
        - If `url` is supplied, use that when running `path` to get token, otherwise
            try to get `url` from OS env vars CF_URL and AX_URL
        - If `token` is supplied, it will be checked for validity
        - If `token` is not supplied, and `env` is True, try to get a token
          from the OS env vars CF_TOKEN
        - If `token` is not supplied or defined in OS env vars
          and `run` is True, try to get a token from the command `$path access token`
        - If `token` is not supplied or defined in OS env vars
          or returned from the command `$path access token` and `login` is True,
          try to get a token from the command `$path access login'

    Args:
        url: URL to use in `access token` and `access login` commands,
            will error if not supplied and OS env vars CF_URL or AX_URL are not defined
        token: access token supplied by user, will be checked for validity if not empty
        env: if no token supplied, try to get token from OS env var CF_TOKEN
        run: if no token supplied or in OS env vars, try to get token from `access token` and
            `access login` commands
        run_access: if run is True, try to get token from `access token`,
        run_login: if run is True and no token returned from `access token` command, try to get
            token from `access login` command
        path: path to cloudflared binary to run, can be full path or path in OS env var $PATH
        timeout_access: timeout for `access token` command in seconds
        timeout_login: timeout for `access login` command in seconds
        error: raise error if an invalid token is found or no token can be found
        error_access: raise exc if `access token` command fails and login is False
        error_login: raise exc if `access login` command fails
        echo: echo commands and results to stderr
        echo_verbose: echo more to stderr

    Returns:
        None or token, depending on `error`
    """
    # we use _ to hide variables from args_str
    _source = functools.partial(args_str, flow_get_token)
    echoer(f"{constants.LOG_START} {_source(locals())}", level="debug", echo=echo_verbose)
    _found = check_is_token(
        value=token, echo=echo_verbose, error_empty=False, source=_source(locals())
    )
    _helps = [constants.HELP_RUN]

    if not _found and env:
        try:
            _found = get_env_token(echo=echo_verbose, error=True, error_empty=False)
        except Exception as exc:
            _helps += [constants.HELP_REMOVE, constants.HELP_SET_ENV_FALSE]
            if error:
                raise GetTokenError(
                    message=[constants.ERR_TOKEN_ENV, f"{exc}"],
                    exception=exc,
                    source=_source(locals()),
                    helps=_helps,
                )
            echoer(
                [constants.ERR_TOKEN_ENV, f"{exc}"],
                level=constants.LEVEL_ERROR_FALSE,
                echo=echo_verbose,
            )

    if not _found and run:
        _found = flow_get_token_cloudflared(
            url=url,
            path=path,
            run_access=run_access,
            run_login=run_login,
            timeout_access=timeout_access,
            timeout_login=timeout_login,
            echo=echo,
            echo_verbose=echo_verbose,
            error=error,
            error_access=error_access,
            error_login=error_login,
        )

    if not _found:
        if not run:
            _helps += [constants.HELP_SET_RUN_TRUE]
        if not run_login:
            _helps += [constants.HELP_SET_RUN_LOGIN_TRUE]
        if not run_access:
            _helps += [constants.HELP_SET_RUN_ACCESS_TRUE]
        if not env:
            _helps += [constants.HELP_SET_ENV_TRUE]

        if error:
            raise GetTokenError(
                message=constants.ERR_RUN_NONE, source=_source(locals()), helps=_helps
            )
        echoer(constants.ERR_RUN_NONE, level=constants.LEVEL_ERROR_FALSE, echo=echo_verbose)
    return _found


def flow_get_token_cloudflared(
    url: t.Optional[str] = None,
    run_access: bool = constants.FLOW_RUN_ACCESS,
    run_login: bool = constants.FLOW_RUN_LOGIN,
    path: constants.PathLike = constants.CF_PATH,
    timeout_access: t.Optional[int] = constants.TIMEOUT_ACCESS,
    timeout_login: t.Optional[int] = constants.TIMEOUT_LOGIN,
    error: bool = constants.FLOW_ERROR,
    error_access: bool = constants.FLOW_ERROR,
    error_login: bool = constants.FLOW_ERROR,
    echo: bool = constants.FLOW_ECHO,
    echo_verbose: bool = constants.FLOW_ECHO_VERBOSE,
) -> t.Optional[str]:
    """Get cf-access-token using `access token` and `access login` commands of cloudflared binary.

    Args:
        url: URL to use in `access token` and `access login` commands,
            will error if not supplied and OS env vars CF_URL or AX_URL are not defined
        run_access: try to get token from `access token` command
        run_login: if no token returned from `access token`, try to run `access login` (which
            should open a browser)
        path: path to cloudflared binary to run, can be full path or path in OS env var $PATH
        timeout_access: timeout for command 'cloudflared access token' in seconds
        timeout_login: timeout for command 'cloudflared access login' in seconds
        error: raise error if no token can be found
        error_access: raise exc if `access token` command fails and login is False
        error_login: raise exc if `access login` command fails
        echo: echo commands and results to stderr
        echo_verbose: echo more to stderr
    """
    _source = functools.partial(args_str, flow_get_token_cloudflared)
    echoer(f"{constants.LOG_START} {_source(locals())}", level="debug", echo=echo_verbose)

    if not url:
        url: str = get_env_url(echo=echo_verbose, error=True, error_empty=False)

    url: t.Optional[str] = check_is_url(
        value=url,
        echo=echo_verbose,
        error=True,
        error_empty=True,
        source=_source(locals()),
    )

    path: pathlib.Path = find_cloudflared(value=path, echo=echo)
    _command_access: t.List[str] = [str(path), *constants.CMD_ACCESS, url]
    _command_login: t.List[str] = [str(path), *constants.CMD_LOGIN, url]
    _found: t.Optional[str] = None

    _helps = [constants.HELP_RUN_MANUAL, f"{join_it(_command_login)}"]
    if not run_login:
        _helps += [constants.HELP_SET_RUN_LOGIN_TRUE]

    # try to get token from `access token` command
    if run_access:
        try:
            _result: subprocess.CompletedProcess = run_command(
                command=_command_access,
                timeout=timeout_access,
                echo=echo,
                error=True,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as _exc:
            # we want to set `login` to False if the error is connection refused or similar
            # cloudflared seems to return 1 for any error, so we have to check the stderr output
            # to see if it contains "login" to know if we should try to log in
            _stderr = get_cmd_stderr(_exc)
            if constants.ACCESS_STDERR_CHECK not in _stderr and run_login:
                echoer(
                    f"{constants.ERR_NO_LOGIN_STDERR}\n{_stderr}",
                    level=constants.LEVEL_ERROR_FALSE,
                    echo=echo,
                )
                run_login = False
            if error_access and not run_login:
                raise GetTokenError(
                    constants.ERR_RUN_ACCESS, exception=_exc, source=_source(locals()), helps=_helps
                ) from _exc
            echoer(constants.ERR_RUN_ACCESS, level=constants.LEVEL_ERROR_FALSE, echo=echo)
        else:
            _found = check_result_is_token(
                result=_result, echo=echo_verbose, error=error_access, error_empty=False
            )

    # try to get token from `access login` command
    if not _found and run_login:
        try:
            _result: subprocess.CompletedProcess = run_command(
                command=_command_login,
                timeout=timeout_login,
                echo=echo,
                error=True,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as _exc:
            if error_login:
                raise GetTokenError(
                    message=constants.ERR_RUN_LOGIN,
                    exception=_exc,
                    source=_source(locals()),
                    helps=_helps,
                ) from _exc
            echoer(constants.ERR_RUN_LOGIN, level=constants.LEVEL_ERROR_FALSE, echo=echo)
        else:
            return check_result_is_token(
                result=_result, echo=echo_verbose, error=error_login, error_empty=error_login
            )

    # if we get here, we didn't find a token
    if not _found:
        if error:
            raise GetTokenError(
                message=constants.ERR_RUN_ACCESS_LOGIN, source=_source(locals()), helps=_helps
            )
        echoer(constants.ERR_RUN_ACCESS_LOGIN, level=constants.LEVEL_ERROR_FALSE, echo=echo_verbose)
    return _found
