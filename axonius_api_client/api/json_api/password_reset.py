# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import Optional, Type, Union

from ...http import Http
from .base import BaseModel, BaseSchema
from .generic import BoolValue


@dataclasses.dataclass
class CreateRequest(BaseModel):
    """Pass."""

    user_id: str
    user_name: str


@dataclasses.dataclass
class SendRequest(BaseModel):
    """Pass."""

    email: str
    user_id: str
    invite: bool = False


@dataclasses.dataclass
class SendResponse(BaseModel):
    """Pass."""

    user_name: str


@dataclasses.dataclass
class ValidateRequest(BaseModel):
    """Pass."""

    token: str

    def dump_request_params(self, **kwargs) -> Optional[dict]:
        """Pass."""
        return None


@dataclasses.dataclass
class ValidateResponse(BoolValue):
    """Pass."""

    @classmethod
    def load_response(
        cls,
        data: Union[dict, list],
        http: Http,
        api_endpoint,
        schema_cls: Optional[Type[BaseSchema]] = None,
        **kwargs,
    ):
        """Pass."""
        data = {"value": data["valid"]}
        return super().load_response(
            data=data, http=http, schema_cls=schema_cls, api_endpoint=api_endpoint, **kwargs
        )
        # PBUG: forced into BoolValue model

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None


@dataclasses.dataclass
class UseRequest(BaseModel):
    """Pass."""

    token: str
    password: str


@dataclasses.dataclass
class UseResponse(BaseModel):
    """Pass."""

    user_name: str
