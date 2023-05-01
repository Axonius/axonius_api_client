# -*- coding: utf-8 -*-
"""Tools for getting OS env vars.

TODO: This whole module needs to be refactored.

It was originally intended as a quick hack to preload
environment variables before importing the whole package
in order to overcome limitations in older versions of python.

get_env_connect should be converted to use click options,
but due to time constraints CONNECT_SCHEMAS is used instead.

We will need to refactor cli/__init__.py so that the Connect
options are defined in a separate module that can be imported
by both cli/__init__.py and setup_env.py
"""
import enum
import logging
import os
import pathlib
import pprint
import sys
import typing as t

import dotenv

LOGGER = logging.getLogger("axonius_api_client.setup_env")
"""Logger to use"""
dotenv.main.logger = LOGGER

YES: t.List[str] = ["1", "true", "t", "yes", "y", "on"]
"""Values that should be considered as true"""

NO: t.List[str] = ["0", "false", "f", "no", "n", "off"]
"""Values that should be considered as false"""

KEY_PRE: str = "AX_"
CF_PRE: str = "CF_"
"""Prefix for axonapi related OS env vars"""

KEY_CF_TOKEN = f"{CF_PRE}TOKEN"
KEY_CF_RUN = f"{CF_PRE}RUN"
KEY_CF_ERROR = f"{CF_PRE}ERROR"
KEY_CF_PATH = f"{CF_PRE}PATH"

CF_TOKEN_DEFAULT = None
CF_PATH_DEFAULT = "cloudflared"
CF_RUN_DEFAULT = "no"
CF_ERROR_DEFAULT = "no"

KEY_DEFAULT_PATH: str = f"{KEY_PRE}PATH"
"""OS env to use for :attr:`DEFAULT_PATH` instead of CWD"""

KEY_ENV_FILE: str = f"{KEY_PRE}ENV_FILE"
"""OS env to use for .env file name"""

KEY_ENV_PATH: str = f"{KEY_PRE}ENV"
"""OS env to use for path to '.env' file"""

KEY_OVERRIDE: str = f"{KEY_PRE}ENV_OVERRIDE"
"""OS env to control ignoring OS env when loading .env file"""

KEY_URL: str = f"{KEY_PRE}URL"
"""OS env to get API URL from"""

KEY_EXTRA_WARN: str = f"{KEY_PRE}EXTRA_WARN"

KEY_KEY: str = f"{KEY_PRE}KEY"
"""OS env to get API key from"""

KEY_SECRET: str = f"{KEY_PRE}SECRET"
"""OS env to get API secret from"""

KEY_FEATURES: str = f"{KEY_PRE}FEATURES"
"""OS env to get API features to enable from"""

KEY_CERTWARN: str = f"{KEY_PRE}CERTWARN"
"""OS env to get cert warning bool from"""

KEY_CERTPATH: str = f"{KEY_PRE}CERTPATH"
"""OS env to get cert warning bool from"""

KEY_DEBUG: str = f"{KEY_PRE}DEBUG"
"""OS env to enable debug logging"""

KEY_DEBUG_PRINT: str = f"{KEY_PRE}DEBUG_PRINT"
"""OS env to use print() instead of LOGGER.debug()"""

KEY_USER_AGENT: str = f"{KEY_PRE}USER_AGENT"
"""OS env to use a custom User Agent string."""

KEY_CREDENTIALS = f"{KEY_PRE}CREDENTIALS"
DEFAULT_CREDENTIALS: str = "no"

DEFAULT_DEBUG: str = "no"
"""Default for :attr:`KEY_DEBUG`"""

DEFAULT_EXTRA_WARN: str = "yes"

DEFAULT_DEBUG_PRINT: str = "no"
"""Default for :attr:`KEY_DEBUG_PRINT`"""

DEFAULT_OVERRIDE: str = "yes"
"""Default for :attr:`KEY_OVERRIDE`"""

DEFAULT_CERTWARN: str = "yes"
"""Default for :attr:`KEY_CERTWARN`"""

DEFAULT_ENV_FILE: str = ".env"
"""Default for :attr:`KEY_ENV_FILE`"""

KEYS_HIDDEN: t.List[str] = [KEY_KEY, KEY_SECRET, KEY_CF_TOKEN]
"""t.List of keys to hide in :meth:`get_env_ax`"""

KEY_MATCHES: t.List[str] = ["password", "secret", "token", "key"]
"""t.List of key partial matches to hide in :meth:`get_env_ax`"""

HIDDEN: str = "_HIDDEN_"
"""Value to use for hidden keys in :meth:`get_env_ax`"""

EMPTY_STRINGS = ["", "none", "null", "nil"]
EMPTY_OBJECTS = [None, [], {}, set(), tuple(), "", b""]


CONNECT_SCHEMAS: dict = {
    "url": {
        "env": KEY_URL,
        "arg": "url",
        "default": None,
        "type": "string",
        "description": "API URL",
        "empty_ok": False,
    },
    "key": {
        "env": KEY_KEY,
        "arg": "key",
        "default": None,
        "type": "string",
        "description": "API Key",
        "empty_ok": False,
    },
    "secret": {
        "env": KEY_SECRET,
        "arg": "secret",
        "default": None,
        "type": "string",
        "description": "API Secret",
        "empty_ok": False,
    },
    "certwarn": {
        "env": KEY_CERTWARN,
        "arg": "certwarn",
        "default": DEFAULT_CERTWARN,
        "type": "boolean",
        "description": "Enable/disable cert warnings",
    },
    "credentials": {
        "env": KEY_CREDENTIALS,
        "arg": "credentials",
        "default": DEFAULT_CREDENTIALS,
        "type": "boolean",
        "description": "Treat key/secret as username/password",
    },
    "cf_token": {
        "env": KEY_CF_TOKEN,
        "arg": "cf_token",
        "default": CF_TOKEN_DEFAULT,
        "type": "string",
        "description": "Cloudflare access token",
        "empty_ok": True,
    },
    "cf_path": {
        "env": KEY_CF_PATH,
        "arg": "cf_path",
        "default": CF_PATH_DEFAULT,
        "type": "string",
        "description": "Path to cloudflared binary to run if cf_run is True",
        "empty_ok": True,
    },
    "cf_run": {
        "env": KEY_CF_RUN,
        "arg": "cf_run",
        "default": CF_RUN_DEFAULT,
        "type": "boolean",
        "description": (
            "If cf_token not supplied, run cloudflared binary in cf_path to get Cloudflare "
            "access token"
        ),
    },
    "cf_error": {
        "env": KEY_CF_ERROR,
        "arg": "cf_error",
        "default": CF_ERROR_DEFAULT,
        "type": "boolean",
        "description": (
            "If cf_token not supplied, raise an error if a token cannot be obtained from "
            "cloudflared binary in cf_path"
        ),
    },
}
# TBD convert to click options (need to refactor cli/__init__.py to do this properly)


def is_empty_object(value: t.Any) -> bool:
    """Check if value is an empty object.

    Args:
        value: value to check

    Returns:
        bool: True if value is an empty object
    """
    return value in EMPTY_OBJECTS


def is_empty_string(value: t.Any) -> bool:
    """Check if value is an empty string.

    Args:
        value: value to check

    Returns:
        bool: True if value is an empty string
    """
    value = bytes_to_str(value)
    is_str = isinstance(value, str) and value.strip()
    return True if not is_str else value.strip().lower() in EMPTY_STRINGS


def is_empty(value: t.Any) -> bool:
    """Check if value is empty.

    Args:
        value: value to check

    Returns:
        bool: True if value is empty
    """
    return is_empty_object(value) or is_empty_string(value)


ENV_NAME = f"dotenv file named {DEFAULT_ENV_FILE!r} (override with ${KEY_ENV_FILE})"


class Results(enum.Enum):
    """Enum for find_dotenv results."""

    supplied: str = "user supplied .env file as find_dotenv(ax_env=...)"
    env_path: str = f"OS environment variable ${KEY_ENV_PATH}"
    default_path: str = f"OS environment variable ${KEY_DEFAULT_PATH} or current working directory"
    find_dotenv_cwd: str = f"Walk to root from the current working directory to find a {ENV_NAME}"
    find_dotenv_script: str = (
        f"Walk to root from the directory of the currently running script to find a {ENV_NAME} "
        "(does not work in interactive mode or `sys.frozen=True`)"
    )
    not_found: str = f"No {ENV_NAME} found"


def spew(
    msg: str,
    debug: t.Optional[bool] = None,
    debug_print: t.Optional[bool] = None,
) -> None:  # pragma: no cover
    """Print a message to stdout."""
    if DEBUG_PRINT is True or debug_print is True:
        print(msg, file=sys.stderr)
    if DEBUG is True or debug is True:
        LOGGER.debug(msg)


def get_file_or_dir_with_file(
    path: t.Union[str, bytes, pathlib.Path], filename: t.Union[str, bytes, pathlib.Path]
) -> t.Optional[pathlib.Path]:
    """Check if path is a file or dir with a file.

    Args:
        path: path to check
        filename: filename to check for

    Returns:
        pathlib.Path: path to file if found, else None
    """
    path = bytes_to_str(path)
    if isinstance(path, str) and path.strip():
        path = pathlib.Path(path.strip()).expanduser().resolve()
    if isinstance(path, pathlib.Path) and path.exists():
        # if it is a dir, append env_file to it
        if path.is_dir():
            path = path / filename
        # TBD: check if file is readable
        # TBD: check file size
        if path.is_file():
            return path
    return None


def find_dotenv(
    ax_env: t.Optional[t.Union[str, bytes, pathlib.Path]] = None,
    filename: t.Optional[str] = DEFAULT_ENV_FILE,
    default: t.Optional[t.Union[str, bytes, pathlib.Path]] = os.getcwd(),
    check_ax_env: bool = True,
    check_default: bool = True,
    check_walk_cwd: bool = True,
    check_walk_script: bool = True,
    debug: bool = True,
) -> t.Tuple[str, str]:
    """Find a .env file.

    Args:
        ax_env: manual path to look for .env file
        filename: name of the .env file to look for (not a path, just a filename),
            override with $AX_ENV_FILE
        default: default path to use if ax_env or $AX_PATH is not supplied (default is CWD)
        check_ax_env: check if $value is file or $value/$filename is file from $AX_ENV
        check_default: check if $value is file or $value/$filename is file $AX_PATH with default
            as default value
        check_walk_cwd: walk to root to find `filename` from current working directory
        check_walk_script: walk to root to find `filename` from running scripts directory
            (does not work in interactive mode or `sys.frozen=True`)
        debug: enable debug output

    Notes:
        Order of operations:
            * Check for ax_env for .env (or dir with .env in it)
            * Check for OS env var :attr:`KEY_ENV_PATH` for .env (or dir with .env in it)
            * Check for OS env var :attr:`KEY_DEFAULT_PATH` as dir with .env in it
            * use dotenv.find_dotenv() to walk tree from CWD
            * use dotenv.find_dotenv() to walk tree from package root
    """
    _spew: callable = lambda x: spew(f"find_dotenv(): {x}", debug)

    # $AX_ENV_FILE=".env"
    # name of the file to look for - should not be a full path
    # just the name of the .env file we will look for by default when
    # a directory is supplied instead of a file for AX_ENV
    filename = get_env_str(key=KEY_ENV_FILE, default=filename)

    _r = Results.supplied
    found: t.Optional[pathlib.Path] = get_file_or_dir_with_file(path=ax_env, filename=filename)
    _spew(f"ax_env={ax_env!r}, found={found!r}, ({_r.value})")
    if found:
        return _r.name, str(found)

    if check_ax_env:
        _r = Results.env_path
        from_ax_env: t.Optional[str] = get_env_str(key=KEY_ENV_PATH, default="", empty_ok=True)
        found: t.Optional[pathlib.Path] = get_file_or_dir_with_file(
            path=from_ax_env, filename=filename
        )
        _spew(f"${KEY_ENV_PATH}={from_ax_env!r}, found={found!r} ({_r.value})")
        if found:
            return _r.name, str(found)

    if check_default:
        _r = Results.default_path
        from_default_path: t.Optional[str] = get_env_str(
            key=KEY_DEFAULT_PATH, default=default, empty_ok=True
        )
        found: t.Optional[pathlib.Path] = get_file_or_dir_with_file(
            path=from_default_path, filename=filename
        )
        _spew(f"${KEY_DEFAULT_PATH}={from_default_path!r}, found={found!r} ({_r.value})")
        if found:
            return _r.name, str(found)

    if check_walk_cwd:
        _r = Results.find_dotenv_cwd
        found_env: t.Optional[str] = dotenv.find_dotenv(filename=filename, usecwd=True)
        _spew(f"found={found_env!r} ({_r.value})")
        if found_env:
            return _r.name, found_env

    if check_walk_script:
        _r = Results.find_dotenv_script
        found_env: t.Optional[str] = dotenv.find_dotenv(filename=filename, usecwd=False)
        _spew(f"found={found_env!r} ({_r.value})")
        if found_env:
            return _r.name, found_env

    _r = Results.not_found
    found: str = ""
    _spew(f"found={found!r} ({_r.value})")
    return _r.name, found


LOADED = {}


class MSG:
    """Messages for :func:`load_dotenv` and :func:`find_dotenv`."""

    not_found = "Could not find"
    already_loaded = "Override is False, not loading already loaded"
    loading = "Loading .env with override"


def load_dotenv(
    ax_env: t.Optional[t.Union[str, bytes, pathlib.Path]] = None,
    override: t.Optional[bool] = None,
    debug: t.Optional[bool] = True,
    verbose: t.Optional[bool] = None,
    **kwargs,
) -> str:
    """Load a '.env' file as environment variables accessible to this package.

    Args:
        ax_env: path to .env file to load, if directory will look for '.env' in that directory
        override: override existing env vars with those in .env file
        debug: enable debug output
        verbose: enable verbose output in dotenv.load_dotenv
        kwargs: additional keyword arguments to pass to :func:`find_dotenv`
    """
    _spew: callable = lambda x: spew(f"load_dotenv(): {x}", debug)

    src, ax_env = find_dotenv(ax_env=ax_env, debug=debug, **kwargs)
    desc = f".env file from {src!r} ax_env={str(ax_env)!r}"

    if not ax_env:
        _spew(f"{MSG.not_found} {desc}")
        return ax_env

    override = (
        override
        if isinstance(override, bool)
        else get_env_bool(key=KEY_OVERRIDE, default=DEFAULT_OVERRIDE)
    )
    load_key = str(ax_env)
    if load_key in LOADED and override is not True:
        loaded = LOADED[load_key]
        src = loaded["src"]
        ax_env = loaded["ax_env"]
        desc = f".env file from {src!r} ax_env={str(ax_env)!r}"
        _spew(f"{MSG.already_loaded} {desc}")
        return str(ax_env)

    LOADED[load_key] = loaded = {
        "src": src,
        "ax_env": ax_env,
        "override": override,
    }
    _spew(f"{MSG.loading} {override} from {src!r} ax_env={str(ax_env)!r}")
    pre = f"{KEY_PRE} and {CF_PRE} env vars"
    loaded["before"] = before = get_env_ax(hide=False)
    _spew(f"{pre} before load dotenv:\n{pprint.pformat(hide_values(before))}")
    dotenv.load_dotenv(dotenv_path=ax_env, verbose=verbose, override=override)
    loaded["after"] = after = get_env_ax(hide=False)
    changed = [k for k in before if k not in after or before[k] != after[k]]
    added = [k for k in after if k not in before]
    _spew(
        f"{pre} after load dotenv changed={changed}, added={added}:\n"
        f"{pprint.pformat(hide_values(after))}"
    )
    return str(ax_env)


def get_env_ax_env() -> str:
    """Get the value of the OS env var :attr:`KEY_ENV_PATH`."""
    return get_env_str(key=KEY_ENV_PATH, default=None, empty_ok=True)


def get_env_str(
    key: str,
    default: t.Any = None,
    empty_ok: bool = False,
    lower: bool = False,
    strip: bool = True,
    description: t.Optional[str] = None,
) -> str:
    """Get an OS env var.

    Args:
        key: OS env key
        default: default to use if not found
        empty_ok: do not throw an exc if the key's value is empty
        lower: lowercase the value
        strip: strip the value
        description: description of the env var

    Raises:
        :exc:`ValueError`: OS env var value is empty and empty_ok is False
    """
    env_value = os.environ.get(key, "")
    is_empty_env = is_empty(env_value)
    resolved = bytes_to_str(default if is_empty_env else env_value)
    resolved = resolved.strip() if strip and isinstance(resolved, str) else resolved
    resolved = resolved.lower() if lower and isinstance(resolved, str) else resolved
    is_empty_resolved = is_empty(resolved)
    if is_empty_resolved and not empty_ok:
        msgs = [
            "Error in OS environment variable",
            f"  Description: {description!r}",
            f"  Is Empty OK?: {empty_ok!r}",
            "",
            f"  OS environment variable Name: {key!r}",
            f"  OS environment variable Value: {env_value!r}",
            f"  OS environment variable Value is empty: {is_empty_env!r}",
            "",
            f"  Default Value: {default!r}",
            f"  Resolved Value: {resolved!r}",
            f"  Resolved Value is empty: {is_empty_resolved!r}",
        ]
        ax_dotenv = get_env_ax_env()
        ax_dot = f'({KEY_ENV_PATH}="{ax_dotenv}")'

        msgs += [
            "",
            f"Must specify {key!r} in .env {ax_dot} file or in OS environment variable, i.e.:",
            f'  {key}="{env_value}"',
        ]
        raise ValueError("\n".join(msgs))
    return resolved


def get_env_bool(key: str, default: t.Any = None, description: t.Optional[str] = None) -> bool:
    """Get an OS env var and turn convert it to a boolean.

    Args:
        key: OS env key
        default: default to use if not found
        description: description of env var for error message

    Raises:
        :exc:`ValueError`: OS env var value is not bool
    """
    value = get_env_str(key=key, default=default, lower=True, description=description)
    if value in YES or value is True:
        return True
    if value in NO or value is False:
        return False
    msg = [
        f"Supplied value {value!r} for OS environment variable {key!r} must be one of:",
        f"  For true: {', '.join(YES)}",
        f"  For false: {', '.join(NO)}",
    ]
    raise ValueError("\n".join(msg))


def get_env_extra_warn(
    ax_env: t.Optional[t.Union[str, bytes, pathlib.Path]] = None,
    **kwargs,
) -> bool:
    """Get AX_CERT_VERIFY from OS env vars.

    Args:
        ax_env: path to .env file to load, if not supplied will find a '.env'
        kwargs: passed to :func:`load_dotenv`
    """
    load_dotenv(ax_env=ax_env, **kwargs)
    return get_env_bool(key=KEY_EXTRA_WARN, default=DEFAULT_EXTRA_WARN)


def get_env_path(
    key: str,
    default: t.Optional[str] = None,
    get_dir: bool = True,
) -> t.Union[pathlib.Path, str]:
    """Get a path from an OS env var.

    Args:
        key: OS env var to get path from
        default: default path to use if OS env var not set
        get_dir: if path is file, return directory containing file
    """
    value = get_env_str(key=key, default=default, empty_ok=True)
    if value:
        value = pathlib.Path(value).expanduser().resolve()
        if get_dir and value.is_file():
            value = value.parent
    return value or ""


def get_env_csv(
    key: str,
    default: t.Optional[str] = None,
    empty_ok: bool = False,
    lower: bool = False,
) -> t.List[str]:
    """Get an OS env var as a CSV.

    Args:
        key: OS env key
        default: default to use if not found
        empty_ok: do not throw an exc if the key's value is empty
        lower: lowercase the value
    """
    value = get_env_str(key=key, default=default, empty_ok=empty_ok, lower=lower)
    value = [y for y in [x.strip() for x in value.split(",")] if y]
    return value


def get_env_user_agent(
    ax_env: t.Optional[t.Union[str, bytes, pathlib.Path]] = None,
    **kwargs: t.Any,
) -> str:
    """Get AX_USER_AGENT from OS env vars.

    Args:
        ax_env: path to .env file to load, if not supplied will find a '.env'
        **kwargs: passed to :func:`load_dotenv`
    """
    load_dotenv(ax_env=ax_env, **kwargs)
    return get_env_str(key=KEY_USER_AGENT, default="", empty_ok=True)


def load_schema(schema: dict, kwargs: t.Optional[dict] = None) -> t.Any:
    """Load a schema from an OS env var."""
    kwargs = {} if not isinstance(kwargs, dict) else kwargs
    arg = schema["arg"]
    schema_type = schema["type"]
    env_key = schema["env"]
    empty_ok = schema.get("empty_ok", False)
    default = kwargs[arg] if arg in kwargs else schema.get("default", None)
    description = schema.get("description", "")

    if schema_type == "boolean":
        return get_env_bool(key=env_key, default=default, description=description)

    return get_env_str(
        key=env_key,
        default=default,
        description=description,
        empty_ok=empty_ok,
    )


def get_env_connect(
    ax_env: t.Optional[t.Union[str, bytes, pathlib.Path]] = None,
    load_override: t.Optional[bool] = None,
    load_filename: t.Optional[str] = DEFAULT_ENV_FILE,
    load_default: t.Optional[t.Union[str, bytes, pathlib.Path]] = os.getcwd(),
    load_check_ax_env: bool = True,
    load_check_default: bool = True,
    load_check_walk_cwd: bool = True,
    load_check_walk_script: bool = True,
    debug: t.Optional[bool] = True,
    **kwargs,
) -> dict:
    """Get connect arguments that start with AX_ or CF_ from OS env vars.

    Notes:
        Arguments are defined in :data:`CONNECT_SCHEMAS`.

    Args:
        ax_env: path to .env file to load, if not supplied will find a '.env'
        debug: if True, will print debug messages
        load_override: if True, will override any existing OS env vars with values
        load_filename: filename to load from
        load_default: default path to use if OS env var not set
        load_check_ax_env: if True, will check for AX_ENV_PATH in OS env vars
        load_check_default: if True, will check for DEFAULT_ENV_FILE in OS env vars
        load_check_walk_cwd: if True, will walk up from cwd looking for DEFAULT_ENV_FILE
        load_check_walk_script: if True, will walk up from script looking for DEFAULT_ENV_FILE
        **kwargs: checked for argument defaults to use instead of schema defaults
    """
    load_dotenv(
        ax_env=ax_env,
        debug=debug,
        override=load_override,
        filename=load_filename,
        default=load_default,
        check_ax_env=load_check_ax_env,
        check_default=load_check_default,
        check_walk_cwd=load_check_walk_cwd,
        check_walk_script=load_check_walk_script,
    )
    return {k: load_schema(v, kwargs) for k, v in CONNECT_SCHEMAS.items()}


def get_env_features(
    ax_env: t.Optional[t.Union[str, bytes, pathlib.Path]] = None,
    **kwargs,
) -> t.List[str]:
    """Get list of features to enable from OS env vars.

    Args:
        ax_env: path to .env file to load, if not supplied will find a '.env'
        kwargs: passed to :func:`load_dotenv`

    """
    load_dotenv(ax_env=ax_env, **kwargs)
    return get_env_csv(key=KEY_FEATURES, default="", empty_ok=True, lower=True)


def hide_value(key: str, value: t.Any) -> t.Any:
    """Hide sensitive values."""
    if key in KEYS_HIDDEN:
        return HIDDEN
    for check in KEY_MATCHES:
        if check in str(key).lower().strip():
            return HIDDEN
    return value


def hide_values(data: dict) -> dict:
    """Hide sensitive values."""
    return {k: hide_value(k, v) for k, v in data.items()}


def get_env_ax(hide: bool = True) -> dict:
    """Get all axonapi related OS env vars."""
    data = {k: v for k, v in os.environ.items() if k.startswith(KEY_PRE) or k.startswith(CF_PRE)}
    return hide_values(data) if hide else data


def set_env(
    key: str,
    value: t.Any,
    ax_env: t.Optional[t.Union[str, bytes, pathlib.Path]] = None,
    quote_mode: str = "always",
    export: bool = False,
    encoding: str = "utf-8",
) -> t.Tuple[t.Optional[bool], str, str]:
    """Set an environment variable in .env file."""
    from . import INIT_DOTENV

    ax_env = ax_env or INIT_DOTENV or DEFAULT_ENV_FILE
    value = str(bytes_to_str(value))
    return dotenv.set_key(
        dotenv_path=ax_env,
        key_to_set=key,
        value_to_set=value,
        quote_mode=quote_mode,
        export=export,
        encoding=encoding,
    )


def bytes_to_str(value: t.Any, encoding: str = "utf-8", errors: str = "ignore") -> t.Any:
    """Convert bytes to str."""
    if isinstance(value, bytes):
        value = value.decode(encoding, errors=errors)
    return value


DEBUG_PRINT: bool = get_env_bool(key=KEY_DEBUG_PRINT, default=DEFAULT_DEBUG_PRINT)
"""Use print() instead of LOGGER.debug()."""

DEBUG: bool = get_env_bool(key=KEY_DEBUG, default=DEFAULT_DEBUG)
"""Enable package wide debugging."""

DEFAULT_PATH: str = str(get_env_path(key=KEY_DEFAULT_PATH, default=os.getcwd()))
"""Default path to use throughout this package"""
