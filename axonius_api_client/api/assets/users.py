# -*- coding: utf-8 -*-
"""API for working with user assets."""
from typing import List

from .asset_mixin import GEN_TYPE, AssetMixin


class Users(AssetMixin):
    """API for working with user assets.

    Examples:
        For all examples for this asset type,
        create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume ``apiobj``
        is ``client.users``

        >>> apiobj = client.users

        * Get count of assets: :meth:`count`
        * Get count of assets from a saved query: :meth:`count_by_saved_query`
        * Get assets: :meth:`get`
        * Get assets from a saved query: :meth:`get_by_saved_query`
        * Get the full data set for a single asset: :meth:`get_by_id`
        * Work with saved queries: :obj:`axonius_api_client.api.assets.saved_query.SavedQuery`
        * Work with fields: :obj:`axonius_api_client.api.assets.fields.Fields`
        * Work with tags: :obj:`axonius_api_client.api.assets.labels.Labels`

    See Also:
        * Device assets :obj:`axonius_api_client.api.assets.devices.Devices`

    """

    ASSET_TYPE: str = "users"

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

    def get_by_usernames(self, values: List[str], **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_USERNAME` in values.

        Args:
            values: list of usernames
            **kwargs: passed to :meth:`get_by_values`
        """
        kwargs["field"] = self.FIELD_USERNAME
        kwargs["field_manual"] = True
        kwargs["values"] = values
        return self.get_by_values(**kwargs)

    def get_by_username_regex(self, value: str, **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_USERNAME` regex matches value.

        Args:
            value: regex of username to match
            **kwargs: passed to :meth:`get_by_value_regex`
        """
        kwargs["field"] = self.FIELD_USERNAME
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value_regex(**kwargs)

    def get_by_username(self, value: str, **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_USERNAME` == value.

        Args:
            value: username
            **kwargs: passed to :meth:`get_by_value`
        """
        kwargs["field"] = self.FIELD_USERNAME
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)

    def get_by_mails(self, values: List[str], **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_MAIL` in values.

        Args:
            values: list of email addressses
            **kwargs: passed to :meth:`get_by_values`
        """
        kwargs["field"] = self.FIELD_MAIL
        kwargs["field_manual"] = True
        kwargs["values"] = values
        return self.get_by_values(**kwargs)

    def get_by_mail_regex(self, value: str, **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_MAIL` regex matches value.

        Args:
            value: regex of email address to match
            **kwargs: passed to :meth:`get_by_value_regex`
        """
        kwargs["field"] = self.FIELD_MAIL
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value_regex(**kwargs)

    def get_by_mail(self, value: str, **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_MAIL` == value.

        Args:
            value: email address
            **kwargs: passed to :meth:`get_by_value`
        """
        kwargs["field"] = self.FIELD_MAIL
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)

    FIELD_USERNAME: str = "specific_data.data.username"
    """User Name field."""

    FIELD_MAIL: str = "specific_data.data.mail"
    """Mail field."""

    FIELD_DOMAIN: str = "specific_data.data.domain"
    """Domain field."""

    FIELD_IS_ADMIN: str = "specific_data.data.is_admin"
    """Is Admin field."""

    FIELD_MAIN: str = FIELD_USERNAME
    """Field name of the main identifier."""

    FIELD_SIMPLE: str = FIELD_USERNAME
    """Field name of a simple field."""

    FIELD_COMPLEX: str = "specific_data.data.associated_devices"
    """Field name of a complex field."""

    FIELD_COMPLEX_SUB: str = "device_caption"
    """Field name of a complex sub field."""

    wizard: str = None
    """:obj:`axonius_api_client.api.wizards.wizard.Wizard`: Query wizard for python objects."""

    wizard_text: str = None
    """:obj:`axonius_api_client.api.wizards.wizard_text.WizardText`: Query wizard for text files."""

    wizard_csv = None
    """:obj:`axonius_api_client.api.wizards.wizard_csv.WizardCsv`: Query wizard for CSV files."""
