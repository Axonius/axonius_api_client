# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import Optional, Type, Union

from ..models import DataModel, DataSchema
from .generic import BoolValue


@dataclasses.dataclass
class CreateRequest(DataModel):
    """Pass."""

    user_id: str
    user_name: str


@dataclasses.dataclass
class SendRequest(DataModel):
    """Pass."""

    email: str
    user_id: str
    invite: bool = False


@dataclasses.dataclass
class SendResponse(DataModel):
    """Pass."""

    user_name: str


@dataclasses.dataclass
class ValidateRequest(DataModel):
    """Pass."""

    token: str

    def dump_request_params(self, **kwargs) -> Optional[dict]:
        """Pass."""
        return None


@dataclasses.dataclass
class ValidateResponse(BoolValue):
    """Pass."""

    @classmethod
    def _load_response(
        cls,
        data: Union[dict, list],
        client,
        api_endpoint,
        schema_cls: Optional[Type[DataSchema]] = None,
        **kwargs,
    ):
        """Pass."""
        data = {"value": data["valid"]}
        return super()._load_response(
            data=data, client=client, schema_cls=schema_cls, api_endpoint=api_endpoint, **kwargs
        )
        # PBUG: forced into BoolValue model

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return None


@dataclasses.dataclass
class UseRequest(DataModel):
    """Pass."""

    token: str
    password: str


@dataclasses.dataclass
class UseResponse(DataModel):
    """Pass."""

    user_name: str
