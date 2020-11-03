# -*- coding: utf-8 -*-
"""Tools for getting OS env vars."""
import logging
import os
import pathlib
from typing import List, Optional, Tuple, Union

import dotenv

LOGGER = logging.getLogger("axonius_api_client.setup_env")
"""Logger to use"""
dotenv.main.logger = LOGGER

YES: List[str] = ["1", "true", "t", "yes", "y", "on"]
"""Values that should be considered as truthy"""

NO: List[str] = ["0", "false", "f", "no", "n", "off"]
"""Values that should be considered as falsey"""

KEY_PRE: str = "AX_"
"""Prefix for axonapi related OS env vars"""

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

KEY_KEY: str = f"{KEY_PRE}KEY"
"""OS env to get API key from"""

KEY_SECRET: str = f"{KEY_PRE}SECRET"
"""OS env to get API secret from"""

KEY_CERTWARN: str = f"{KEY_PRE}CERTWARN"
"""OS env to get cert warning bool from"""

KEY_DEBUG: str = f"{KEY_PRE}DEBUG"
"""OS env to enable debug logging"""

KEY_DEBUG_PRINT: str = f"{KEY_PRE}DEBUG_PRINT"
"""OS env to use print() instead of LOGGER.debug()"""

DEFAULT_DEBUG: str = "no"
"""Default for :attr:`KEY_DEBUG`"""

DEFAULT_DEBUG_PRINT: str = "no"
"""Default for :attr:`KEY_DEBUG_PRINT`"""

DEFAULT_OVERRIDE: str = "yes"
"""Default for :attr:`KEY_OVERRIDE`"""

DEFAULT_CERTWARN: str = "yes"
"""Default for :attr:`KEY_CERTWARN`"""

DEFAULT_ENV_FILE: str = ".env"
"""Default for :attr:`KEY_ENV_FILE`"""

KEYS_HIDDEN: List[str] = [KEY_KEY, KEY_SECRET]
"""List of keys to hide in :meth:`get_env_ax`"""

HIDDEN: str = "_HIDDEN_"
"""Value to use for hidden keys in :meth:`get_env_ax`"""


def find_dotenv(
    ax_env: Optional[Union[str, pathlib.Path]] = None, default: str = os.getcwd()
) -> Tuple[str, str]:
    """Find a .env file.

    Args:
        ax_env: manual path to look for .env file
        default: default path to use if :attr:`KEY_DEFAULT_PATH` is not set

    Notes:
        Order of operations:

            * Check for ax_env for .env (or dir with .env in it)
            * Check for OS env var :attr:`KEY_ENV_PATH` for .env (or dir with .env in it)
            * Check for OS env var :attr:`KEY_DEFAULT_PATH` as dir with .env in it
            * use dotenv.find_dotenv() to walk tree from CWD
            * use dotenv.find_dotenv() to walk tree from package root
    """
    env_file = get_env_str(key=KEY_ENV_FILE, default=DEFAULT_ENV_FILE)
    if ax_env:
        found_env = pathlib.Path(ax_env).expanduser().resolve()
        found_env = found_env / env_file if found_env.is_dir() else found_env
        if found_env.is_file():
            return "supplied", str(found_env)

    found_env = get_env_path(key=KEY_ENV_PATH, get_dir=False)
    if found_env and found_env.exists():
        found_env = found_env / env_file if found_env.is_dir() else found_env
        if found_env.is_file():
            return "env_path", str(found_env)

    found_env = get_env_path(key=KEY_DEFAULT_PATH, default=default)
    if found_env and found_env.exists():
        found_env = found_env / env_file if found_env.is_dir() else found_env
        if found_env.is_file():
            return "default_path", str(found_env)

    found_env = dotenv.find_dotenv(filename=env_file, usecwd=True) or ""
    if found_env and pathlib.Path(found_env).is_file():
        return "find_dotenv_cwd", found_env

    found_env = dotenv.find_dotenv(filename=env_file, usecwd=False) or ""
    if found_env and pathlib.Path(found_env).is_file():
        return "find_dotenv_pkg", found_env

    return "not_found", ""


def load_dotenv(ax_env: Optional[Union[str, pathlib.Path]] = None, **kwargs) -> str:
    """Load a '.env' file as environment variables accessible to this package.

    Args:
        ax_env: path to .env file to load, if directory will look for '.env' in that directory
        **kwargs: passed to dotenv.load_dotenv()
    """
    src, ax_env = find_dotenv(ax_env=ax_env)

    override = get_env_bool(key=KEY_OVERRIDE, default=DEFAULT_OVERRIDE)
    DEBUG_LOG(f"Loading .env with override {override} from {src!r} {str(ax_env)!r}")
    if pathlib.Path(ax_env).is_file():
        DEBUG_LOG(f"{KEY_PRE}.* env vars before load dotenv: {get_env_ax()}")
        dotenv.load_dotenv(dotenv_path=ax_env, verbose=DEBUG, override=override)
        DEBUG_LOG(f"{KEY_PRE}.* env vars after load dotenv: {get_env_ax()}")
    return ax_env


def get_env_bool(key: str, default: Optional[bool] = None) -> bool:
    """Get an OS env var and turn convert it to a boolean.

    Args:
        key: OS env key
        default: default to use if not found

    Raises:
        :exc:`ValueError`: OS env var value is not able to be converted to bool
    """
    value = get_env_str(key=key, default=default, lower=True)
    if value in YES:
        return True

    if value in NO:
        return False

    msg = [
        f"Supplied value {value!r} for OS environment variable {key!r} must be one of:",
        f"  For true: {', '.join(YES)}",
        f"  For false: {', '.join(NO)}",
    ]
    raise ValueError("\n".join(msg))


def get_env_str(
    key: str, default: Optional[str] = None, empty_ok: bool = False, lower: bool = False
) -> str:
    """Get an OS env var.

    Args:
        key: OS env key
        default: default to use if not found
        lower: lowercase the value

    Raises:
        :exc:`ValueError`: OS env var value is empty and empty_ok is False
    """
    orig_value = os.environ.get(key, "").strip()
    value = orig_value

    if default is not None and value in [None, ""]:
        value = default

    if not empty_ok and value in [None, ""]:
        raise ValueError(
            f"OS environment variable {key!r} is empty with value {orig_value!r}\n"
            f"Must specify {key!r} in .env file or in OS environment variable"
        )

    value = value.lower() if lower and isinstance(value, str) else value
    return value


def get_env_path(
    key: str, default: Optional[str] = None, get_dir: bool = True
) -> Union[pathlib.Path, str]:
    """Get a path from an OS env var.

    Args:
        key: OS env var to get path from
        default: default path to use if OS env var not set
        get_dir: return directory containing file of path is file
    """
    value = get_env_str(key=key, default=default, empty_ok=True)
    if value:
        value = pathlib.Path(value).expanduser().resolve()
        if get_dir and value.is_file():
            value = value.parent
    return value or ""


def get_env_connect(**kwargs) -> dict:
    """Get URL, API key, API secret, and certwarn from OS env vars.

    Args:
        **kwargs: passed to :meth:`load_dotenv`
    """
    load_dotenv(**kwargs)
    return {
        "url": get_env_str(key=KEY_URL),
        "key": get_env_str(key=KEY_KEY),
        "secret": get_env_str(key=KEY_SECRET),
        "certwarn": get_env_bool(key=KEY_CERTWARN, default=DEFAULT_CERTWARN),
    }


def get_env_ax():
    """Get all axonapi related OS env vars."""
    value = {k: v for k, v in os.environ.items() if k.startswith(KEY_PRE)}
    value = {k: HIDDEN if k in KEYS_HIDDEN else v for k, v in value.items()}
    return value


DEBUG_PRINT: bool = get_env_bool(key=KEY_DEBUG_PRINT, default=DEFAULT_DEBUG_PRINT)
"""Use print() instead of LOGGER.debug()."""

DEBUG_USE = print if DEBUG_PRINT else LOGGER.debug
"""use print or LOGGER.debug()"""

DEBUG: bool = get_env_bool(key=KEY_DEBUG, default=DEFAULT_DEBUG)
"""Enable package wide debugging."""

DEBUG_LOG = DEBUG_USE if DEBUG else lambda x: x
"""Function to use for debug logging"""

DEFAULT_PATH: str = str(get_env_path(key=KEY_DEFAULT_PATH, default=os.getcwd()))
"""Default path to use throughout this package"""
