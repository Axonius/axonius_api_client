"""Tools."""
import subprocess
import shutil
import logging
import os
import types
import typing as t
import pathlib

import click

from . import constants

LOGGER: logging.Logger = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def args_str(
    source: t.Any,
    value: dict,
    prefix: str = "",
    joiner: str = "\n",
    skips: t.Any = None,
    skip_self: bool = True,
    skip_dunder: bool = True,
    skip_upper: bool = True,
    skip_callable: bool = True,
    skip_types: t.Optional[t.Iterable[t.Type]] = None,
    key_prefix: str = constants.KEY_PREFIX,
) -> str:
    """Return str of args for logging.

    Args:
        source: source of args
        value: dict of args
        prefix: prefix to add to str
        joiner: joiner to use for str
        skips: keys to skip
        skip_self: skip key "self"
        skip_dunder: skip keys that start with "_"
        skip_upper: skip keys that are all uppercase
        skip_callable: skip keys that are callable
        skip_types: skip keys that are instances of these types
        key_prefix: prefix to add to each key

    Returns:
        str: str of args for logging
    """
    skips: t.List[str] = listify(skips)
    skip_types: t.Tuple[type] = tuple(listify(skip_types))
    value = {
        k: v
        for k, v in value.items()
        if not (
            k in skips
            or (skip_self and k == "self")
            or (skip_dunder and k.startswith("_"))
            or (skip_upper and k.isupper())
            or (skip_callable and callable(v))
            or (skip_types and isinstance(v, skip_types))
        )
    }
    if callable(source) and getattr(source, "__name__", ""):
        source = source.__name__

    return dict_to_str(
        value=value,
        prefix=f"{prefix}{source} with arguments:\n",
        joiner=joiner,
        key_prefix=key_prefix,
    )


def listify(value: t.Any = None, consume: bool = False) -> t.Union[list, types.GeneratorType]:
    """Coerce any value into a list.

    Args:
        value: value to coerce where None=[], list=value, tuple=list(value), set=list(value),
            generator=list(value) if consume else value, anything_else=[value]
        consume: consume generators and return a list
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    if isinstance(value, types.GeneratorType):
        return list(value) if consume else value
    return [value]


def dict_to_str(
    value: dict,
    prefix: str = "\n",
    joiner: str = "\n",
    key_prefix: str = constants.KEY_PREFIX,
) -> str:
    """Convert a dict to a string.

    Args:
        value: dict to convert
        prefix: prefix to add to each line
        joiner: string to join lines with
        key_prefix: prefix to add to each key

    Returns:
        str: converted dict
    """
    return prefix + joiner.join(f"{key_prefix}{k}: {v}" for k, v in value.items())


def get_env_path_raw() -> str:
    """Get PATH env var."""
    return os.environ.get(constants.PATH_ENV, "")


def get_env_path() -> t.List[str]:
    """Get paths from PATH env var."""
    return get_env_path_raw().split(os.path.pathsep)


def get_env_path_str() -> str:
    """Get paths from PATH env var as a string."""
    paths = get_env_path() or constants.PATHS_NOT_FOUND
    value = [constants.PATH_HEADER, *paths]
    return "\n".join(value)


def get_cmd_stderr(value: t.Any) -> str:
    """Get stderr from subprocess result."""
    return coerce_str(getattr(value, "stderr", ""))


def get_cmd_stdout(value: t.Any) -> str:
    """Get stdout from subprocess result."""
    return coerce_str(getattr(value, "stdout", ""))


def get_cmd_command(value: t.Any) -> str:
    """Get cmd from subprocess result."""
    return join_it(getattr(value, "cmd", getattr(value, "args", [])))


def get_cmd_exit_code(value: t.Any) -> t.Optional[int]:
    """Get returncode from subprocess result."""
    return getattr(value, "returncode", None)


def get_cmd_timeout(value: t.Any) -> t.Optional[int]:
    """Get timeout from subprocess result."""
    return getattr(value, "timeout", None)


def get_cmd_strs(
    value: t.Any,
    stdout: bool = True,
    stderr: bool = True,
    command: bool = True,
    exit_code: bool = True,
) -> t.List[str]:
    """Get cmd output and code from subprocess result."""
    items = []
    if stdout:
        items.extend([f"--> STDOUT", f"{get_cmd_stdout(value)}"])
    if stderr:
        items.extend([f"--> STDERR", f"{get_cmd_stderr(value)}"])
    if command:
        items.extend([f"--> COMMAND", f"{get_cmd_command(value)}"])
    if exit_code:
        items.extend([f"--> EXIT CODE: {get_cmd_exit_code(value)}"])
    return items


def join_it(*args: t.Any, joiner: str = " ") -> str:
    """Join a command to a string."""
    items = []
    for arg in args:
        items.extend([str(x) for x in listify(arg)])
    return joiner.join(items)


def bytes_to_str(
    value: t.Any,
    encoding: str = "utf-8",
    ignore: bool = True,
    replace: bool = True,
    errors: t.Optional[str] = None,
) -> t.Any:
    """Convert bytes to str if needed.

    Args:
        value: token to convert if is bytes
        encoding: encoding to use
        ignore: set `errors` to ignore, overrides `replace`
        replace: set `errors` to replace, overridden by `ignore`
        errors: errors to use, defaults to 'strict' if ignore and replace are False

    Returns:
        token converted to str if needed
    """
    if isinstance(value, bytes):
        if not isinstance(errors, str):
            if ignore:
                errors = "ignore"
            elif replace:
                errors = "replace"
            else:
                errors = "strict"
        return value.decode(encoding, errors=errors)
    return value


def strip_it(value: t.Any, *args) -> t.Any:
    """Strip a token if it has a strip method."""
    return value.strip(*args) if callable(getattr(value, "strip", None)) else value


def coerce_str(value: t.Any, strip: bool = True) -> str:
    """Convert from anything to str.

    Args:
        value: token to convert
        strip: call strip_it on token before returning

    Returns:
        token converted to str
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(bytes_to_str(value))
    if strip:
        value = strip_it(value)
    return value


def coerce_path(value: t.Any, expand: bool = True, resolve: bool = True) -> pathlib.Path:
    """Coerce a token into a string then into an expanded and resolved path.

    Args:
        value: token to coerce into str and then pathlib.Path
        expand: call expanduser() on the path
        resolve: call resolve() on the path

    Returns:
        token coerced into str and then pathlib.Path
    """
    check = coerce_str(value)
    path = pathlib.Path(check) if check else pathlib.Path()
    if expand:
        path = path.expanduser()
    if resolve:
        path = path.resolve()
    return path


def is_executable(value: t.Any) -> bool:
    """Check if a token is an executable.

    Args:
        value: token to coerce into str and then path to check

    Returns:
        True if token is an executable, False otherwise
    """
    # noinspection PyBroadException
    try:
        return os.access(str(coerce_path(value)), os.X_OK)
    except Exception:  # pragma: no cover
        return False


def is_file(value: t.Any) -> bool:
    """Check if a token is a file.

    Args:
        value: token to coerce into str and then path to check is_file()

    Returns:
        True if token is a file, False otherwise
    """
    # noinspection PyBroadException
    try:
        return coerce_path(value).is_file()
    except Exception:  # pragma: no cover
        return False


def is_token(value: t.Any, length: t.Optional[int] = constants.TOKEN_LENGTH) -> bool:
    """Check if a value is valid cloudflare access token (>= length).

    Args:
        value: token to check if it is a valid cloudflare access token
        length: length to check token against

    Returns:
        if value is a valid cloudflare access token
    """
    check = strip_it(bytes_to_str(value))
    if isinstance(check, str) and check:
        if isinstance(length, int):
            return len(check) >= length
        return True
    return False


def is_url(value: t.Any, length: t.Optional[int] = constants.URL_LENGTH) -> bool:
    """Check if a value is a valid url (>= length).

    Args:
        value: value to check
        length: length to check value against

    Returns:
        if value is a valid url
    """
    check = coerce_str(value)
    if isinstance(check, str) and check:
        if isinstance(length, int):
            return len(check) > length
        return True
    return False


def echoer(
    message: t.Union[str, t.Iterable[str]],
    level: str = constants.ECHO_LEVEL,
    echo: bool = constants.ECHO,
    style: bool = constants.ECHO_STYLE,
    prefix: bool = constants.ECHO_PREFIX,
    stderr: bool = constants.ECHO_STDERR,
    log: bool = constants.ECHO_LOG,
    logger: logging.Logger = LOGGER,
    exc_info: bool = constants.ECHO_EXC_INFO,
    **kwargs,
) -> None:
    """Log and echo a message.

    Args:
        message: message to log and/or echo
        level: log level to use
        echo: echo the message to stdout
        style: style the message with `click.style`
        prefix: prefix the message with a level prefix
        stderr: echo the message to stderr instead of stdout
        log: log the message
        logger: logger to use for logging
        exc_info: include exception info in log
        kwargs: passed to `click.style` and `click.echo`
    """
    message = "\n".join([str(x) for x in listify(message)])

    level = str(level).lower().strip()
    if log or not echo:
        getattr(logger, level)(message, exc_info=exc_info)

    if echo:
        if style:
            level_style: dict = constants.LEVEL_STYLES.get(level, constants.LEVEL_STYLES[""])
            if prefix:
                level_prefix: str = constants.LEVEL_PREFIXES.get(
                    level, constants.LEVEL_PREFIXES[""]
                )
                message = f"{level_prefix}{message}"
            style_args: dict = {k: kwargs[k] for k in constants.STYLE_ARGS if k in kwargs}
            style_args.update({k: v for k, v in level_style.items() if k not in style_args})
            style_args.update({"text": message})
            message = click.style(**style_args)

        echo_args: dict = {k: kwargs[k] for k in constants.ECHO_ARGS if k in kwargs}
        echo_args.update({"err": stderr, "message": message})
        click.echo(**echo_args)


def get_env_token(
    keys: t.Union[str, t.Iterable[str]] = constants.TOKEN_ENVS,
    echo: bool = constants.FLOW_ECHO_VERBOSE,
    error: bool = constants.ERROR,
    error_empty: bool = False,
    length: t.Optional[int] = constants.TOKEN_LENGTH,
) -> t.Optional[str]:
    """Get token from an environment variable.

    Args:
        keys: name of the environment variable to get
        echo: echo the token to stdout
        error: raise ValueError if the token is found but is not a valid token
        error_empty: raise ValueError if the token is not found
        length: length of the token to check against

    Returns:
        token of the environment variable if found and is a valid token, None otherwise

    Raises:
        ValueError: if the environment variable is found but is not a valid token or is not found
    """
    return check_env(
        checker=check_is_token,
        desc="token",
        keys=keys,
        echo=echo,
        error=error,
        error_empty=error_empty,
        length=length,
    )


def get_env_url(
    keys: t.Union[str, t.Iterable[str]] = constants.URL_ENVS,
    echo: bool = constants.FLOW_ECHO_VERBOSE,
    error: bool = constants.ERROR,
    error_empty: bool = True,
    length: t.Optional[int] = constants.URL_LENGTH,
) -> t.Optional[str]:
    """Get url from an environment variable.

    Args:
        keys: name of the environment variable to get
        echo: echo the url to stdout
        error: raise ValueError if the url is found but is not a valid url
        error_empty: raise ValueError if the url is not found
        length: length of the url to check against

    Returns:
        url of the environment variable if found and is a valid url, None otherwise

    Raises:
        ValueError: if the environment variable is found but is not a valid url
    """
    return check_env(
        checker=check_is_url,
        desc="url",
        keys=keys,
        echo=echo,
        error=error,
        error_empty=error_empty,
        length=length,
    )


def check_env(
    checker: t.Callable,
    desc: str,
    keys: t.Union[str, t.Iterable[str]],
    echo: bool = constants.FLOW_ECHO_VERBOSE,
    error: bool = constants.ERROR,
    error_empty: bool = False,
    length: t.Optional[int] = constants.TOKEN_LENGTH,
) -> t.Any:
    """Run a checker function against a list of environment variables."""
    keys = listify(keys)
    count = len(keys) - 1
    for index, key in enumerate(keys):
        is_last = index == count
        value = coerce_str(os.environ.get(key, ""))
        check = checker(
            value=value,
            error=error,
            echo=echo,
            source=f"environment variable {key!r} out of keys {keys!r}",
            error_empty=error_empty if is_last else False,
            length=length,
        )
        if check:
            return check

    echoer(f"No {desc} found in environment variables {keys!r}", echo=echo)
    return None


def check_is_file(
    value: constants.PathLike, source: t.Optional[str] = None, desc: str = "file"
) -> pathlib.Path:
    """Check if a value is a file.

    Args:
        value: path to check
        source: source of the value, used for error messages
        desc: description of the value, used for error messages

    Returns:
        pathlib.Path to the file if found

    Raises:
        FileNotFoundError: if the file is not found
    """
    source = source or f"token={value!r}, type={type(value).__name__}"
    found = coerce_path(value)
    if found.is_file():
        return found

    raise FileNotFoundError(
        f"{constants.ERR_FILE_NOT_FOUND} {desc} from {source}: {found!r}"
    )


def check_is_file_executable(
    value: constants.PathLike,
    source: t.Optional[str] = None,
    desc: str = "file",
) -> pathlib.Path:
    """Check if a value is a file and is executable.

    Args:
        value: path to check
        source: source of the value, used for error messages
        desc: description of the value, used for error messages

    Returns:
        pathlib.Path to the file if found and executable

    Raises:
        FileNotFoundError: if the file is not found or is not executable
    """
    source = source or f"value={value!r}, type={type(value).__name__}"
    found = check_is_file(value=value, desc=desc, source=source)
    if is_executable(found):
        return found

    raise FileNotFoundError(
        f"{constants.ERR_FILE_NOT_EXECUTABLE} {desc} from {source}: {found!r}"
    )


def check_is_url(
    value: t.Any,
    source: t.Any = None,
    error_empty: bool = True,
    error: bool = constants.ERROR,
    echo: bool = constants.FLOW_ECHO_VERBOSE,
    length: t.Optional[int] = constants.URL_LENGTH,
) -> t.Optional[str]:
    """Check if a URL is valid.

    Args:
        value: url to check
        source: source of url
        error: raise ValueError if url is not valid
        error_empty: raise ValueError if url is empty
        echo: echo the checks
        length: minimum length of url to check

    Returns:
        url if it is valid or None if error is False

    Raises:
        ValueError: if error is True and the url is not valid
    """
    source: t.Any = source or f"value={value!r}, type={type(value).__name__}"
    check: t.Optional[str] = coerce_str(value)
    is_empty: bool = not check
    is_valid: bool = is_url(check, length=length) if not is_empty else False

    valid: str = "valid" if is_valid else "invalid"
    desc: str = f"{valid} url from {source} (length={len(check)}, valid length={length})"
    action: str = "Found"

    if not is_valid:
        if error and (not is_empty or (is_empty and error_empty)):
            raise ValueError(f"{action} {desc}\n{constants.ERR_TRY_URL}")
        action = "Ignoring"
        check = None

    echoer(f"{action} {desc}", echo=echo)
    return check


def check_is_token(
    value: t.Any,
    source: t.Any = None,
    error_empty: bool = True,
    error: bool = constants.ERROR,
    echo: bool = constants.FLOW_ECHO_VERBOSE,
    length: t.Optional[int] = constants.TOKEN_LENGTH,
) -> t.Optional[str]:
    """Check if a token can be considered a valid cloudflare access token.

    Args:
        value: token to check
        source: source of the token, used for echo and error messages
        error: raise ValueError if token is not a valid cloudflare access token
        error_empty: raise ValueError if token is empty
        echo: echo the check output to stderr
        length: minimum length of token to check

    Returns:
        token if it is a valid cloudflare access (greater than length)

    Raises:
        ValueError: if the token is not a valid cloudflare access token
    """
    source: t.Any = source or f"value={value!r}, type={type(value).__name__}"
    check: str = coerce_str(value)
    _length: int = len(check)
    is_empty: bool = not bool(check)
    is_valid: bool = is_token(check, length=length)
    info: str = f"cloudflare access token of length {_length} [valid={length}] from {source}"

    final_error: bool = error

    if is_valid:
        msg = constants.ERR_TOKEN_FOUND
        level = "debug"
        final_error = False
    else:
        if is_empty:
            msg = constants.ERR_TOKEN_NOT_FOUND
            level: str = "error" if final_error else "warning"
            if not error_empty:
                final_error = False
                level = "debug"
        else:
            msg = constants.ERR_TOKEN_FOUND_INVALID
            level = "error" if final_error else "warning"

    echoer(f"{msg} {info}", echo=echo, level=level)
    if error and final_error:
        raise ValueError(f"{msg} {info}")

    return check if is_valid else None


def check_result_is_token(
    result: t.Union[
        subprocess.CompletedProcess, subprocess.CalledProcessError, subprocess.TimeoutExpired
    ],
    echo: bool = constants.FLOW_ECHO_VERBOSE,
    error: bool = True,
    error_empty: bool = True,
    length: t.Optional[int] = constants.TOKEN_LENGTH,
) -> t.Optional[str]:
    """Check if the last line of stdout contains a valid cloudflare access token.

    Args:
        result: result of a subprocess.run() call
        echo: echo the checks
        error: raise ValueError if token is not a valid cloudflare access token
        error_empty: raise ValueError if token is empty
        length: minimum length of token to check

    Returns:
        token if it is a valid cloudflare access (greater than length)
    """
    stdout = get_cmd_stdout(result)
    stderr = get_cmd_stderr(result)
    cmd = get_cmd_command(result)
    exit_code = get_cmd_exit_code(result)
    token = ""

    source = f"the STDOUT of command `{cmd}` with exit code {exit_code}"
    if stderr:
        source += f" and STDERR:\n{stderr}"

    stdout_lines: t.List[str] = [x.strip() for x in stdout.strip().splitlines() if x.strip()]
    if stdout_lines:
        token = stdout_lines[-1]

    return check_is_token(
        value=token,
        source=source,
        echo=echo,
        error=error,
        error_empty=error_empty,
        length=length,
    )


def which(value: constants.PathLike) -> t.Optional[pathlib.Path]:
    """Find an executable in $PATH, mirrors unix `which` command.

    Args:
        value: path to pass to shutil.which()

    Returns:
        pathlib.Path to the executable if found, None otherwise
    """
    found: t.Optional[constants.PathLike] = shutil.which(value)
    return coerce_path(value=found) if found else None


def find_cloudflared(
    value: constants.PathLike = constants.CF_PATH,
    echo: bool = constants.ECHO,
) -> pathlib.Path:
    """Find the executable for cloudflared.

    Args:
        value: path to pass to which() to find the executable in $PATH
         or to check_is_file_executable() to check if it is a file and executable
        echo: echo the path to stdout

    Returns:
        pathlib.Path to the cloudflared executable
    """
    if isinstance(value, pathlib.Path):
        return check_is_file_executable(value=value)

    value = strip_it(bytes_to_str(value))

    found = which(value=value)
    source = "from $PATH"

    if not found:
        found = coerce_path(value=value)
        source = "from path of file"

    try:
        found: pathlib.Path = check_is_file_executable(
            value=found, source=source, desc="cloudflared binary"
        )
        echoer(f"Found executable binary as path to file: {found!r}", echo=echo)
    except FileNotFoundError as exc:
        msgs = [f"{exc}", get_env_path_str(), constants.CF_INSTALL]
        raise FileNotFoundError("\n\n".join(msgs)) from exc
    return found


def run_command(
    command: t.Union[str, t.Iterable[str]],
    timeout: t.Optional[int] = constants.TIMEOUT,
    error: bool = constants.ERROR,
    echo: bool = constants.ECHO,
    include_output: bool = constants.RUN_INCLUDE_OUTPUT,
    capture_output: bool = constants.RUN_CAPTURE_OUTPUT,
    text: bool = constants.RUN_TEXT,
) -> subprocess.CompletedProcess:
    """Run a command and return the result.

    Notes:
        Patches __str__ methods for :exc:`subprocess.CalledProcessError` and
        :exc:`subprocess.TimeoutExpired` to use a better error message that
        includes stdout and stderr.

    Args:
        command: command to run
        error: raise :exc:`subprocess.CalledProcessError` if return code is not 0
        timeout: raise :exc:`subprocess.TimeoutExpired` if command takes longer than timeout
        echo: echo the command to stdout
        include_output: patch subprocess errors to include stdout and stderr
        capture_output: tell subprocess to capture stdout and stderr
        text: tell subprocess to decode stdout and stderr as text

    Returns:
        subprocess.CompletedProcess result from :meth:`subprocess.run`
    """
    patch_subprocess(include_output=include_output)
    echoer(f"Running command with timeout={timeout}, error={error}:\n{join_it(command)}", echo=echo)
    result = subprocess.run(
        command, capture_output=capture_output, text=text, check=error, timeout=timeout
    )
    return result


def patch_subprocess(include_output: bool = constants.RUN_INCLUDE_OUTPUT):
    """Patch subprocess to add new string methods that include stdout & stderr.

    Args:
        include_output: enable or disable the patch

    Examples:
        >>> from axonius_api_client cf_token
        >>> cf_token.tools.run_command(["ls", "--aaa"], include_output=True)

    """
    if include_output:
        subprocess.CalledProcessError.__str__ = _called_str_patched
        subprocess.TimeoutExpired.__str__ = _timeout_str_patched
    else:
        subprocess.CalledProcessError.__str__ = _called_str_original
        subprocess.TimeoutExpired.__str__ = _timeout_str_original


_called_str_original: t.Callable = subprocess.CalledProcessError.__str__
_timeout_str_original: t.Callable = subprocess.TimeoutExpired.__str__


def _called_str_patched(self):
    """New string method for CalledProcess."""
    errors = [
        "Command returned a non-zero exit code.",
        *get_cmd_strs(self),
    ]
    return "\n".join(errors)


def _timeout_str_patched(self):
    """New string method for TimeoutExpired."""
    errors = [
        f"Command took longer than the timeout of {get_cmd_timeout(self)}",
        *get_cmd_strs(self),
    ]
    return "\n".join(errors)
