# -*- coding: utf-8 -*-
"""Models for API requests & responses."""

import dataclasses
from typing import List, Optional, Union

from ..data import BaseData


@dataclasses.dataclass
class ApiResponse(BaseData):
    """Pass."""

    data: Union[dict, List[dict]]
    meta: Optional[dict] = None


@dataclasses.dataclass
class FeatureFlags(ApiResponse):
    """Pass."""

    @property
    def config(self) -> dict:
        """Pass."""
        return self.data["attributes"]["config"]

    @property
    def schema(self) -> dict:
        """Pass."""
        return self.data["meta"]["schema"]
