# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from typing import Generator, List, Union

from ..routers import API_VERSION, Router
from .asset_mixin import AssetMixin


class Users(AssetMixin):
    """User related API methods."""

    FIELD_USERNAME: str = "specific_data.data.username"
    FIELD_MAIL: str = "specific_data.data.mail"
    FIELD_DOMAIN: str = "specific_data.data.domain"
    FIELD_IS_ADMIN: str = "specific_data.data.is_admin"
    FIELD_SIMPLE: str = FIELD_USERNAME
    FIELD_COMPLEX: str = "specific_data.data.associated_devices"
    FIELD_COMPLEX_SUB: str = "device_caption"

    FIELDS_SPECIFIC: List[str] = [
        FIELD_USERNAME,
        FIELD_DOMAIN,
        FIELD_MAIL,
        FIELD_IS_ADMIN,
    ]

    @property
    def fields_default(self) -> List[str]:
        """Fields to use by default for getting assets."""
        return [
            self.FIELD_ADAPTERS,
            self.FIELD_USERNAME,
            self.FIELD_DOMAIN,
            self.FIELD_MAIL,
            self.FIELD_IS_ADMIN,
            self.FIELD_LAST_SEEN,
            self.FIELD_TAGS,
        ]

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.users

    def get_by_usernames(
        self, values: List[str], **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where username in values."""
        kwargs["field"] = self.FIELD_USERNAME
        kwargs["field_manual"] = True
        kwargs["values"] = values
        return self.get_by_values(**kwargs)

    def get_by_username_regex(
        self, value: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where username regex matches value."""
        kwargs["field"] = self.FIELD_USERNAME
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value_regex(**kwargs)

    def get_by_username(
        self, value: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where username == value."""
        kwargs["field"] = self.FIELD_USERNAME
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)

    def get_by_mails(
        self, values: List[str], **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where mail in values."""
        kwargs["field"] = self.FIELD_MAIL
        kwargs["field_manual"] = True
        kwargs["values"] = values
        return self.get_by_values(**kwargs)

    def get_by_mail_regex(
        self, value: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where mail regex matches value."""
        kwargs["field"] = self.FIELD_MAIL
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value_regex(**kwargs)

    def get_by_mail(self, value: str, **kwargs) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where mail == value."""
        kwargs["field"] = self.FIELD_MAIL
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)
