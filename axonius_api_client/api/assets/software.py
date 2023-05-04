# -*- coding: utf-8 -*-
"""API for working with user assets."""
from typing import List

from .asset_mixin import AssetMixin


class Software(AssetMixin):
    """API for working with the asset type 'software'.

    TODO: this is a stub place holder for now
    """

    ASSET_TYPE: str = "software"

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
