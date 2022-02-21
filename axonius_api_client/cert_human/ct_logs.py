# -*- coding: utf-8 -*-
"""Fallback for all_logs_list.json."""
import datetime
import json
import logging
import pathlib
from typing import Union

import cachetools
import requests

from .all_logs_list import FALLBACK_JSON, FALLBACK_UPDATED
from .paths import pathify

LOG: logging.Logger = logging.getLogger(__name__)
CACHE = cachetools.LRUCache(maxsize=1)

URL: str = "https://www.gstatic.com/ct/log_list/v2/all_logs_list.json"
LOGS_FILE: str = "all_logs_list.json"
LOGS_PATH = pathlib.Path(__file__).parent / LOGS_FILE
REFETCH: bool = False
MAX_DAYS: int = 30


@cachetools.cached(cache=CACHE)
def load(
    path: Union[str, pathlib.Path] = LOGS_PATH,
    refetch: bool = REFETCH,
    max_days: int = MAX_DAYS,
    **kwargs,
) -> dict:
    """Pass."""
    path = pathify(path=path)
    is_past_max = False
    mtime = None
    days = None
    data = None
    exists = path.is_file()
    if exists:
        mtime = datetime.datetime.fromtimestamp(path.lstat().st_mtime)
        delta = datetime.datetime.now() - mtime
        days = delta.days
        is_past_max = isinstance(max_days, int) and days >= max_days

    info = [
        f"path='{path}'",
        f"modified_time='{mtime}'",
        f"modified_days={days}",
        f"refetch={refetch}",
        f"exists={exists}",
        f"max_days={max_days}",
        f"is_past_max_days={is_past_max}",
    ]
    info = ", ".join(info)

    if not exists or is_past_max:
        refetch = True
        LOG.debug(f"{info}: forcing refetch=True due to exists=False or is_past_max=True")

    if refetch:
        LOG.debug(f"{info}: refetching")
        try:
            data = requests.get(URL, **kwargs).json()
        except Exception as exc:
            LOG.exception(f"{info}: failed to refetch: {exc}")
        else:
            LOG.debug(f"{info}: refetched, writing data")
            try:
                with path.open("w") as fh:
                    json.dump(data, fh, indent=4)
            except Exception as exc:
                LOG.exception(f"{info} failed to write: {exc}")

    if not data:
        LOG.debug(f"{info}: loading data")
        try:
            with path.open("r") as fh:
                data = json.load(fh)
        except Exception as exc:
            LOG.exception(
                f"{info}: failed to read: {exc}, loading fallback data from {FALLBACK_UPDATED}"
            )
            data = json.loads(FALLBACK_JSON)
    return data
