# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ....exceptions import ApiError
from ..generic import Metadata, MetadataSchema


class LoginResponseSchema(MetadataSchema):
    """Schema for receiving a login response."""

    class Meta:
        """Pass."""

        type_ = "metadata_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return LoginResponse


SCHEMA = LoginResponseSchema()


@dataclasses.dataclass
class LoginResponse(Metadata):
    """Model for receiving a login response."""

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[LoginResponseSchema] = SCHEMA

    META_ACCESS: t.ClassVar[str] = "access_token"
    META_REFRESH: t.ClassVar[str] = "refresh_token"
    COOKIE_ACCESS: t.ClassVar[str] = "ax_access"
    COOKIE_REFRESH: t.ClassVar[str] = "ax_refresh"
    TOKENS: t.ClassVar[t.Dict[str, t.Dict[str, str]]] = {
        "access": {"meta": META_ACCESS, "cookie": COOKIE_ACCESS},
        "refresh": {"meta": META_REFRESH, "cookie": COOKIE_REFRESH},
    }

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return LoginResponseSchema

    @property
    def cookies(self) -> t.Mapping[str, t.Any]:
        """Get the cookies from the response that generated this object."""
        response = getattr(self, "RESPONSE", None)
        cookies = getattr(response, "cookies", {})
        return {} if not hasattr(cookies, "get") else cookies

    @property
    def access_token(self) -> str:
        """Get the Access token for use in auth header."""
        return self.get_token(token="access")

    def get_token(self, token: str):
        """Get token for use in auth header."""
        token_map: dict = self.TOKENS[token]
        meta_key: str = token_map["meta"]
        cookie_key: str = token_map["cookie"]
        meta_val: t.Optional[str] = self.document_meta.get(meta_key)
        cookie_val: t.Optional[str] = self.cookies.get(cookie_key)

        if isinstance(meta_val, str):
            return meta_val

        if isinstance(cookie_val, str):
            return cookie_val

        meta_keys: t.List[str] = list(self.document_meta)
        cookie_keys: t.List[str] = list(self.cookies)

        errs: t.List[str] = [
            f"Unable to find {token} token",
            f"{meta_key!r}: {meta_val!r} in document_meta with keys {meta_keys}",
            f"{cookie_key!r}: {cookie_val!r} in response cookies with keys {cookie_keys}",
        ]
        raise ApiError(errs)

    @property
    def refresh_token(self) -> t.Optional[str]:
        """Get the Refresh token for use in auth header."""
        return self.get_token(token="refresh")

    @property
    def authorization(self) -> str:
        """Get the token to use in the authorization header."""
        return f"Bearer {self.access_token}"

    @property
    def headers(self) -> t.Dict[str, str]:
        """Get the headers to use in requests."""
        return {"authorization": self.authorization}

    @property
    def http_args(self) -> t.Dict[str, t.Dict[str, str]]:
        """Get the HTTP arguments to use in requests."""
        return {"headers": self.headers}
