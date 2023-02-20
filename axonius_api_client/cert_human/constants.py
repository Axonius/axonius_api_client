# -*- coding: utf-8 -*-
"""Fallback for all_logs_list.json."""
import pathlib
from typing import Optional, Tuple


class CT_LOGS:
    """Pass."""

    refetch: bool = False
    modified_days_max: Optional[int] = 30
    timeout: Tuple[float, float] = (3.2, 6.2)

    url: str = "https://www.gstatic.com/ct/log_list/v3/all_logs_list.json"
    data_file: str = "all_logs_list.json"
    path: pathlib.Path = pathlib.Path(__file__).parent / data_file
    request_args: dict = {}

    @classmethod
    def get(cls, key: str, kwargs: dict):
        """Pass."""
        return kwargs.get(key, getattr(cls, key))
