# -*- coding: utf-8 -*-
"""Fallback for all_logs_list.json."""
import json
import logging
from typing import Optional, Tuple

import cachetools
import requests

from .all_logs_list import FALLBACK_JSON, FALLBACK_UPDATED
from .constants import CT_LOGS
from .paths import FileInfo, pathify

LOG: logging.Logger = logging.getLogger(__name__)
CACHE = cachetools.LRUCache(maxsize=10)


@cachetools.cached(cache=CACHE)
def load_ct_logs(**kwargs) -> dict:
    """Pass."""
    kwargs["value"] = pathify(path=CT_LOGS.get(key="path", kwargs=kwargs))

    refetch = calc_refetch(**kwargs)
    data = None

    if refetch:
        kwargs["data"] = data = refetch_data(**kwargs)
        write_data(**kwargs)

    if not data:
        data = read_data(**kwargs)

    if not data:
        data = read_data_fallback(**kwargs)
    return data


def read_data(**kwargs) -> Optional[dict]:
    """Pass."""
    path = pathify(path=CT_LOGS.get(key="path", kwargs=kwargs))

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


def read_data_fallback(**kwargs) -> dict:
    """Pass."""
    LOG.debug(f"Reading fallback data updated on {FALLBACK_UPDATED}")
    data = json.loads(FALLBACK_JSON)
    return data


def write_data(data: Optional[dict], **kwargs) -> bool:
    """Pass."""
    path = pathify(path=CT_LOGS.get(key="path", kwargs=kwargs))

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


def refetch_data(**kwargs) -> Optional[dict]:
    """Pass."""
    url: str = CT_LOGS.get(key="url", kwargs=kwargs)
    timeout: Tuple[float, float] = CT_LOGS.get(key="timeout", kwargs=kwargs)
    request_args: dict = CT_LOGS.get(key="request_args", kwargs=kwargs)

    LOG.debug(f"Refetching data from URL {url!r}")
    try:
        response = requests.get(url, timeout=timeout, **request_args)
        data = response.json()
    except Exception as exc:
        LOG.exception(f"Failed to refetch data from URL {url!r}: {exc}")
        return None
    else:
        LOG.debug(f"Refetched data from URL {url!r}")
        return data


def calc_refetch(**kwargs) -> bool:
    """Pass."""
    path = pathify(path=CT_LOGS.get(key="path", kwargs=kwargs))
    finfo = FileInfo(path=path)

    days_max: Optional[int] = CT_LOGS.get(key="modified_days_max", kwargs=kwargs)
    refetch: bool = CT_LOGS.get(key="refetch", kwargs=kwargs)

    LOG.debug(f"Calculating refetch for {finfo} refetch={refetch}, modified_days_max={days_max}")

    if not refetch and not finfo.exists:
        LOG.debug(f"Forcing refetch=True for {finfo} due to exists=False")
        return True

    if not refetch and finfo.exists and finfo.is_modified_days_ago(value=days_max):
        LOG.debug("Forcing refetch=True for {finfo} due to modified_days_max={days_max}")
        return True

    return refetch
