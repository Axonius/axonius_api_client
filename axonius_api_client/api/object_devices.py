# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import routers
from . import object_mixins
from .. import models


class Devices(models.ApiModel, object_mixins.UserDeviceMixins):
    """Device related API methods."""

    @property
    def _router(self):
        """Router for this API client.

        Returns:
            :obj:`axonius_api_client.api.routers.Router`

        """
        return routers.ApiV1.devices

    @property
    def _default_fields(self):
        """Fields to set as default for methods with fields as kwargs.

        Returns:
            :obj:`dict`

        """
        return {
            "generic": [
                "adapters",
                "labels",
                "specific_data.data.hostname",
                "specific_data.data.network_interfaces.ips",
                "specific_data.data.last_seen",
            ]
        }

    def get_by_name(self, value, **kwargs):
        """Get objects by name using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "specific_data.data.username".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        kwargs.setdefault("field", "specific_data.data.hostname")
        kwargs.setdefault("field_adapter", "generic")
        kwargs["value"] = value
        return self.get_by_field_value(**kwargs)

    # TODO: get_by_ip
    # TODO: get_by_in_subnet
    # TODO: get_by_not_in_subnet
    def get_by_mac(self, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "specific_data.data.network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs.setdefault("field", "specific_data.data.network_interfaces.mac")
        kwargs.setdefault("field_adapter", "generic")
        kwargs["value"] = value
        return self.get_by_field_value(**kwargs)
