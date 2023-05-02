# -*- coding: utf-8 -*-
"""API for working with device assets."""
import ipaddress
from typing import List

from .asset_mixin import GEN_TYPE, AssetMixin


class Devices(AssetMixin):
    """API for working with device assets.

    Examples:
        For all examples for this asset type,
        create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume ``apiobj``
        is ``client.devices``

        >>> apiobj = client.devices

        * Get count of assets: :meth:`count`
        * Get count of assets from a saved query: :meth:`count_by_saved_query`
        * Get assets: :meth:`get`
        * Get assets from a saved query: :meth:`get_by_saved_query`
        * Get the full data set for a single asset: :meth:`get_by_id`
        * Work with saved queries: :obj:`axonius_api_client.api.assets.saved_query.SavedQuery`
        * Work with fields: :obj:`axonius_api_client.api.assets.fields.Fields`
        * Work with tags: :obj:`axonius_api_client.api.assets.labels.Labels`

    See Also:
        * User assets :obj:`axonius_api_client.api.assets.users.Users`
    """

    ASSET_TYPE: str = "devices"

    @property
    def fields_default(self) -> List[str]:
        """Fields to use by default for getting assets."""
        return [
            self.FIELD_ADAPTERS,
            self.FIELD_ASSET_NAME,
            self.FIELD_HOSTNAME,
            self.FIELD_LAST_SEEN,
            self.FIELD_IP,
            self.FIELD_MAC,
            self.FIELD_OS_TYPE,
            self.FIELD_TAGS,
        ]

    def get_by_hostnames(self, values: List[str], **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_HOSTNAME` in values.

        Args:
            values: list of hostnames
            **kwargs: passed to :meth:`get_by_values`
        """
        kwargs["field"] = self.FIELD_HOSTNAME
        kwargs["field_manual"] = True
        kwargs["values"] = values
        return self.get_by_values(**kwargs)

    def get_by_hostname_regex(self, value: str, **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_HOSTNAME` regex matches value.

        Args:
            value: regex of hostname to match
            **kwargs: passed to :meth:`get_by_value_regex`
        """
        kwargs["field"] = self.FIELD_HOSTNAME
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value_regex(**kwargs)

    def get_by_hostname(self, value: str, **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_HOSTNAME` == value.

        Args:
            value: hostname
            **kwargs: passed to :meth:`get_by_value`
        """
        kwargs["field"] = self.FIELD_HOSTNAME
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)

    def get_by_macs(self, values: List[str], **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_MAC` in values.

        Args:
            values: list of mac addresss
            **kwargs: passed to :meth:`get_by_values`
        """
        kwargs["field"] = self.FIELD_MAC
        kwargs["field_manual"] = True
        kwargs["values"] = values
        return self.get_by_values(**kwargs)

    def get_by_mac_regex(self, value: str, **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_MAC` regex matches value.

        Args:
            value: regex of mac adress to match
            **kwargs: passed to :meth:`get_by_value_regex`
        """
        kwargs["field"] = self.FIELD_MAC
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value_regex(**kwargs)

    def get_by_mac(self, value: str, **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_MAC` == value.

        Args:
            value: mac adress
            **kwargs: passed to :meth:`get_by_value`
        """
        kwargs["field"] = self.FIELD_MAC
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)

    def get_by_ips(self, values: List[str], **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_IP` in values.

        Args:
            values: list of ip address
            **kwargs: passed to :meth:`get_by_values`
        """
        kwargs["field"] = self.FIELD_IP
        kwargs["field_manual"] = True
        kwargs["values"] = values
        return self.get_by_values(**kwargs)

    def get_by_ip_regex(self, value: str, **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_IP` regex matches value.

        Args:
            values: regex of ip address to match
            **kwargs: passed to :meth:`get_by_value_regex`
        """
        kwargs["field"] = self.FIELD_IP
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value_regex(**kwargs)

    def get_by_ip(self, value: str, **kwargs) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where :attr:`FIELD_IP` == value.

        Args:
            value: ip address
            **kwargs: passed to :meth:`get_by_value`
        """
        kwargs["field"] = self.FIELD_IP
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)

    def get_by_subnet(
        self, value: str, not_flag: bool = False, pre: str = "", post: str = "", **kwargs
    ) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where ip address is in :attr:`FIELD_IP_RAW`.

        Args:
            value: subnet
            **kwargs: passed to :meth:`get`
        """
        field = self.FIELD_IP_RAW

        network = ipaddress.ip_network(value)
        gte = int(network.network_address)
        lte = int(network.broadcast_address)
        match = "".join(['match({"$gte": ', str(gte), ', "$lte": ', str(lte), "})"])

        inner = f"{field} == {match}"

        kwargs["query"] = self._build_query(
            inner=inner,
            pre=pre,
            post=post,
            not_flag=not_flag,
        )

        return self.get(**kwargs)

    FIELD_ASSET_NAME: str = "specific_data.data.name"
    """Asset Name field."""

    FIELD_HOSTNAME: str = "specific_data.data.hostname"
    """Hostname field."""

    FIELD_IP: str = "specific_data.data.network_interfaces.ips"
    """Network Interfaces IPs field."""

    FIELD_IP_RAW: str = "specific_data.data.network_interfaces.ips_raw"
    """Network Interfaces IPs raw field."""

    FIELD_MAC: str = "specific_data.data.network_interfaces.mac"
    """Network Interfaces MACs field."""

    FIELD_SUBNET: str = "specific_data.data.network_interfaces.subnets"
    """Network Interfaces Subnets field."""

    FIELD_OS_TYPE: str = "specific_data.data.os.type"
    """OS Type field."""

    FIELD_MAIN: str = FIELD_HOSTNAME
    """Field name of the main identifier."""

    FIELD_SIMPLE: str = FIELD_HOSTNAME
    """Field name of a simple field."""

    FIELD_COMPLEX: str = "specific_data.data.network_interfaces"
    """Field name of a complex field."""

    FIELD_COMPLEX_SUB: str = "name"
    """Field name of a complex sub field."""

    wizard: str = None
    """:obj:`axonius_api_client.api.wizards.wizard.Wizard`: Query wizard for python objects."""

    wizard_text: str = None
    """:obj:`axonius_api_client.api.wizards.wizard_text.WizardText`: Query wizard for text files."""

    wizard_csv = None
    """:obj:`axonius_api_client.api.wizards.wizard_csv.WizardCsv`: Query wizard for CSV files."""
