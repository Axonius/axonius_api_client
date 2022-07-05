# -*- coding: utf-8 -*-
"""API for working with user assets."""
from typing import List

from .asset_mixin import AssetMixin


class Vulnerabilities(AssetMixin):
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

    ASSET_TYPE: str = "vulnerabilities"

    @property
    def fields_default(self) -> List[str]:
        """Fields to use by default for getting assets."""
        return [
            self.FIELD_ADAPTERS,
            self.FIELD_LAST_SEEN,
            self.FIELD_TAGS,
        ]

    wizard: str = None
    """:obj:`axonius_api_client.api.wizards.wizard.Wizard`: Query wizard for python objects."""

    wizard_text: str = None
    """:obj:`axonius_api_client.api.wizards.wizard_text.WizardText`: Query wizard for text files."""

    wizard_csv = None
    """:obj:`axonius_api_client.api.wizards.wizard_csv.WizardCsv`: Query wizard for CSV files."""
