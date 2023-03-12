# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ...http import Http
from .base import BaseModel
from .generic import BoolValue


@dataclasses.dataclass
class CreateRequest(BaseModel):
    """Pass."""

    user_id: str
    user_name: str

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass
class SendRequest(BaseModel):
    """Pass."""

    email: str
    user_id: str
    invite: bool = False

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass
class SendResponse(BaseModel):
    """Pass."""

    user_name: str

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass
class ValidateRequest(BaseModel):
    """Pass."""

    token: str

    def dump_request_params(self, **kwargs) -> t.Optional[dict]:
        """Pass."""
        return None

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass
class ValidateResponse(BoolValue):
    """Pass."""

    @classmethod
    def load_response(
        cls, data: t.Union[dict, list], http: Http, schema_cls: t.Any = None, **kwargs
    ):
        """Pass."""
        data = {"value": data["valid"]}
        return super().load_response(data=data, http=http, schema_cls=schema_cls, **kwargs)
        # PBUG: forced into BoolValue model

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass
class UseRequest(BaseModel):
    """Pass."""

    token: str
    password: str

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass
class UseResponse(BaseModel):
    """Pass."""

    user_name: str
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None
