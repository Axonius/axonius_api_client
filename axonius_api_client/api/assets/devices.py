# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import ipaddress
from typing import Generator, List, Union

from ..routers import API_VERSION, Router
from .asset_mixin import AssetMixin


class Devices(AssetMixin):
    """Device related API methods."""

    FIELD_HOSTNAME: str = "specific_data.data.hostname"
    FIELD_IP: str = "specific_data.data.network_interfaces.ips"
    FIELD_IP_RAW: str = "specific_data.data.network_interfaces.ips_raw"
    FIELD_MAC: str = "specific_data.data.network_interfaces.mac"
    FIELD_SUBNET: str = "specific_data.data.network_interfaces.subnets"

    @property
    def fields_default(self) -> List[str]:
        """Fields to use by default for getting assets."""
        return self.FIELDS_API + [
            self.FIELD_HOSTNAME,
            self.FIELD_IP,
            self.FIELD_MAC,
            self.FIELD_SUBNET,
        ]

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.devices

    def get_by_hostnames(
        self, values: List[str], **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where hostname in values."""
        kwargs["field"] = self.FIELD_HOSTNAME
        kwargs["field_manual"] = True
        kwargs["values"] = values
        return self.get_by_values(**kwargs)

    def get_by_hostname_regex(
        self, value: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where hostname regex matches value."""
        kwargs["field"] = self.FIELD_HOSTNAME
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value_regex(**kwargs)

    def get_by_hostname(
        self, value: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where hostname == value."""
        kwargs["field"] = self.FIELD_HOSTNAME
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)

    def get_by_macs(
        self, values: List[str], **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where mac in values."""
        kwargs["field"] = self.FIELD_MAC
        kwargs["field_manual"] = True
        kwargs["values"] = values
        return self.get_by_values(**kwargs)

    def get_by_mac_regex(
        self, value: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where mac regex matches value."""
        kwargs["field"] = self.FIELD_MAC
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value_regex(**kwargs)

    def get_by_mac(
        self, value: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where mac == value."""
        kwargs["field"] = self.FIELD_MAC
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)

    def get_by_ips(
        self, values: List[str], **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where ip in values."""
        kwargs["field"] = self.FIELD_IP
        kwargs["field_manual"] = True
        kwargs["values"] = values
        return self.get_by_values(**kwargs)

    def get_by_ip_regex(
        self, value: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where ip regex matches value."""
        kwargs["field"] = self.FIELD_IP
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value_regex(**kwargs)

    def get_by_ip(
        self, value: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where ip == value."""
        kwargs["field"] = self.FIELD_IP
        kwargs["field_manual"] = True
        kwargs["value"] = value
        return self.get_by_value(**kwargs)

    def get_by_subnet(
        self, value: str, not_flag: bool = False, pre: str = "", post: str = "", **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where ip in subnet.

        Args:
            value (:obj:`str`): value to that must match field
                "network_interfaces.ips_raw"
            **kwargs: passed to :meth:`AssetMixin.get`

        Yields:
            :obj:`dict`: asset matching query that is built if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching query that is built
                if generator is False
        """
        field = self.FIELD_IP_RAW

        network = ipaddress.ip_network(value)
        gte = int(network.network_address)
        lte = int(network.broadcast_address)
        match = "".join(['match({"$gte": ', str(gte), ', "$lte": ', str(lte), "})"])

        inner = f"{field} == {match}"

        kwargs["query"] = self._build_query(
            inner=inner, pre=pre, post=post, not_flag=not_flag,
        )

        return self.get(**kwargs)
