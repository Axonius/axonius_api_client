# -*- coding: utf-8 -*-
"""Constants."""
import logging
import os
import pathlib
from typing import Optional, Tuple, Union

import dotenv

logger = logging.getLogger("ax_setup_env")


PATH_KEY: str = "AX_PATH"
ENV_KEY: str = "AX_ENV"
"""Environment variable to use to override path to '.env' file"""
ENV_OVERRIDE_KEY: str = "AX_ENV_OVERRIDE"
URL_KEY: str = "AX_URL"
KEY_KEY: str = "AX_KEY"
SECRET_KEY: str = "AX_SECRET"

DEFAULT_PATH: str = os.environ.get(PATH_KEY, "").strip() or os.getcwd()
"""Default path to use throughout this package"""


def load_dotenv(
    ax_env: Optional[Union[str, pathlib.Path]] = None, **kwargs
) -> Tuple[str, pathlib.Path]:
    """Load a '.env' file as environment variables accessible to this package.

    Args:
        ax_env: path to .env file to load, if directory will look for '.env' in that directory
        **kwargs: passed to dotenv.load_dotenv()
    """
    ax_env = os.environ.get(ENV_KEY, "").strip() or ax_env

    if not ax_env:
        ax_env = dotenv.find_dotenv()
        logger.debug(f"Found .env file at {ax_env}")

    ax_env = pathlib.Path(ax_env).expanduser().resolve()
    if ax_env.is_dir():
        ax_env = ax_env / ".env"

    logger.debug(f"loading .env file at {ax_env}")
    return (
        dotenv.load_dotenv(dotenv_path=str(ax_env), **kwargs),
        ax_env,
    )


def get_connect_env(**kwargs) -> dict:
    """Pass."""
    override = not os.environ.get(ENV_OVERRIDE_KEY, "").lower().strip() in ["n", "no", "false", "f"]
    kwargs["override"] = override = bool(kwargs.pop("override", override))
    logger.debug(f"Loading .env with override {override}")
    load_dotenv(**kwargs)

    ax_url = os.environ.get(URL_KEY)
    ax_key = os.environ.get(KEY_KEY)
    ax_secret = os.environ.get(SECRET_KEY)

    err = "in .env file or in OS environment variable"
    if not ax_url:
        raise Exception(f"Must specify URL of Axonius {err} {URL_KEY}")

    if not ax_key:
        raise Exception(f"Must specify API key {err} {KEY_KEY}")

    if not ax_secret:
        raise Exception(f"Must specify API secret {err} {SECRET_KEY}")

    return {"url": ax_url, "key": ax_key, "secret": ax_secret}
