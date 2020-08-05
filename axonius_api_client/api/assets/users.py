# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from typing import Generator, List, Union

from ..routers import API_VERSION, Router
from .asset_mixin import AssetMixin


class Users(AssetMixin):
    """User related API methods."""

    FIELD_USERNAME: str = "specific_data.data.username"
    FIELD_MAIL: str = "specific_data.data.mail"

    @property
    def fields_default(self) -> List[str]:
        """Fields to use by default for getting assets."""
        return self.FIELDS_API + [self.FIELD_USERNAME, self.FIELD_MAIL]

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

    def get_by_mail(
        self, value: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where mail == value."""
        kwargs["field"] = self.FIELD_MAIL
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)
