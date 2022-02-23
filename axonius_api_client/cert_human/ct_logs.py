# -*- coding: utf-8 -*-
"""Fallback for all_logs_list.json."""
import datetime
import json
import logging
import pathlib
from typing import Optional, Tuple

import cachetools
import requests

from .all_logs_list import FALLBACK_JSON, FALLBACK_UPDATED
from .paths import PathLike, pathify

LOG: logging.Logger = logging.getLogger(__name__)
CACHE = cachetools.LRUCache(maxsize=1)

URL: str = "https://www.gstatic.com/ct/log_list/v2/all_logs_list.json"
TIMEOUT: Tuple[float, float] = (6.0, 12.0)

LOGS_FILE: str = "all_logs_list.json"
LOGS_PATH: pathlib.Path = pathlib.Path(__file__).parent / LOGS_FILE
REFETCH: bool = False
MAX_DAYS: int = 30


class FileInfo:
    """Pass."""

    def __init__(self, path: PathLike, modified_days_max: Optional[int] = MAX_DAYS):
        """Pass."""
        self.path: pathlib.Path = pathify(path=path)
        self.modified_days_max: Optional[int] = modified_days_max

    @property
    def modified_dt(self) -> Optional[datetime.datetime]:
        """Pass."""
        return datetime.datetime.fromtimestamp(self.path.lstat().st_mtime) if self.exists else None

    @property
    def modified_delta(self) -> Optional[datetime.timedelta]:
        """Pass."""
        return (datetime.datetime.now() - self.modified_dt) if self.exists else None

    @property
    def modified_days(self) -> Optional[int]:
        """Pass."""
        return self.modified_delta.days if self.exists else None

    @property
    def is_past_modified_days_max(self) -> bool:
        """Pass."""
        return (
            self.exists
            and isinstance(self.modified_days_max, int)
            and self.modified_days >= self.modified_days_max
        )

    @property
    def exists(self) -> bool:
        """Pass."""
        return self.path.is_file()

    def __str__(self) -> str:
        """Pass."""
        info = [
            f"path={str(self.path)!r}",
            f"exists={self.exists}",
            f"modified_dt={str(self.modified_dt)!r}",
            f"modified_days={self.modified_days}",
            f"modified_days_max={self.modified_days_max}",
            f"is_past_modified_days_max={self.is_past_modified_days_max}",
        ]
        info = ", ".join(info)
        return f"{self.__class__.__name__}({info})"

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()

    def calc_refetch(self, refetch: bool = REFETCH):
        """Pass."""
        if not refetch and not self.exists:
            LOG.debug("Forcing refetch due to exists=False")
            refetch = True

        if not refetch and self.is_past_modified_days_max:
            LOG.debug("Forcing refetch due to is_past_modified_days_max=True")
            refetch = True
        return refetch


@cachetools.cached(cache=CACHE)
def load(
    path: PathLike = LOGS_PATH, refetch: bool = REFETCH, modified_days_max: int = MAX_DAYS, **kwargs
) -> dict:
    """Pass."""
    finfo = FileInfo(path=path, modified_days_max=modified_days_max)
    LOG.debug(f"Loading data for {finfo}")

    refetch = finfo.calc_refetch(refetch=refetch)
    data = None

    if refetch:
        data = refetch_data(**kwargs)
        write_data(path=path, data=data)

    if not data:
        data = read_data(path=finfo.path)

    if not data:
        data = read_data_fallback()
    return data


def read_data(path: PathLike = LOGS_PATH) -> Optional[dict]:
    """Pass."""
    path = pathify(path=path)
    if path.is_file():
        LOG.debug(f"Reading data from {str(path)!r}")
        try:
            with path.open("r") as fh:
                data = json.load(fh)
        except Exception as exc:
            LOG.exception(f"Failed to read data from {str(path)!r}: {exc}")
            return None
        else:
            return data
    else:
        LOG.warning(f"Unable to read data from {str(path)!r}, file not found")
        return None


def read_data_fallback() -> dict:
    """Pass."""
    LOG.debug(f"Reading fallback data updated on {FALLBACK_UPDATED}")
    data = json.loads(FALLBACK_JSON)
    return data


def write_data(data: Optional[dict], path: PathLike = LOGS_PATH) -> bool:
    """Pass."""
    path = pathify(path=path)

    if isinstance(data, dict) and isinstance(data.get("operators"), list):
        LOG.debug(f"Writing data to {str(path)!r}")
        try:
            path.touch()
            with path.open("w") as fh:
                json.dump(data, fh, indent=4)
        except Exception as exc:
            LOG.exception(f"Failed to write data to {str(path)!r}: {exc}")
            return False
        else:
            LOG.debug(f"Data written to {str(path)!r}")
            return True
    else:
        LOG.warning(f"Data must be dict with 'operators' key, can not write to {str(path)!r}")
        return False


def refetch_data(
    url: str = URL, timeout: Tuple[float, float] = TIMEOUT, **kwargs
) -> Optional[dict]:
    """Pass."""
    LOG.debug(f"Refetching data from URL {url!r}")
    try:
        response = requests.get(url, timeout=timeout, **kwargs)
        data = response.json()
    except Exception as exc:
        LOG.exception(f"Failed to refetch data from URL {url!r}: {exc}")
        return None
    else:
        LOG.debug(f"Refetched data from URL {url!r}")
        return data
