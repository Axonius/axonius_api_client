# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import models


class ApiUsers(models.ApiBase, models.ModelMixins):
    """User related API methods."""

    @property
    def _obj_route(self):
        """Get the object route.

        Returns:
            :obj:`str`

        """
        return "users"

    @property
    def _default_fields(self):
        """Fields to set as default for methods with **fields.

        Returns:
            :obj:`dict`

        """
        return {
            "generic": [
                "adapters",
                "labels",
                "specific_data.data.username",
                "specific_data.data.last_seen",
            ]
        }

    @property
    def _all_fields(self):
        """Fields to use for methods with all_fields.

        Returns:
            :obj:`list` of :obj:`str`

        """
        return ["specific_data.data"]

    @property
    def _name_field(self):
        """Get the field to use in :meth:`axonius_api_client.ModelMixins.get_by_name`.

        Returns:
            :obj:`str`

        """
        return "specific_data.data.username"

    @property
    def _api_version(self):
        """Get the API version to use.

        Returns:
            :obj:`int`

        """
        return 1

    @property
    def _api_path(self):
        """Get the API path to use.

        Returns:
            :obj:`str`

        """
        return "api/V{version}/".format(version=self._api_version)


class ApiDevices(models.ApiBase, models.ModelMixins):
    """Device related API methods."""

    @property
    def _obj_route(self):
        """Get the object route.

        Returns:
            :obj:`str`

        """
        return "devices"

    @property
    def _default_fields(self):
        """Fields to set as default for methods with **fields.

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

    @property
    def _all_fields(self):
        """Fields to use for methods with all_fields.

        Returns:
            :obj:`list` of :obj:`str`

        """
        return ["specific_data.data"]

    @property
    def _name_field(self):
        """Get the field to use in :meth:`axonius_api_client.ModelMixins.get_by_name`.

        Returns:
            :obj:`str`

        """
        return "specific_data.data.hostname"

    @property
    def _api_version(self):
        """Get the API version to use.

        Returns:
            :obj:`int`

        """
        return 1

    @property
    def _api_path(self):
        """Get the API path to use.

        Returns:
            :obj:`str`

        """
        return "api/V{version}/".format(version=self._api_version)
