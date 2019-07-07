# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import models


class ApiUsers(models.ApiBase, models.ModelMixins):
    """User related API methods."""

    _API_VERSION = 1
    """:obj:`int`: Version of the API this ApiBase is made for."""

    _API_PATH = "api/V{version}/".format(version=_API_VERSION)
    """:obj:`str`: Base path of API."""

    DEFAULT_FIELDS = {
        "generic": [
            "adapters",
            "labels",
            "specific_data.data.username",
            "specific_data.data.last_seen",
        ]
    }
    """:obj:`dict`: Fields to set as default for methods with **fields."""

    @property
    def _obj_route(self):
        """Get the object route."""
        return "users"


class ApiDevices(models.ApiBase, models.ModelMixins):
    """Device related API methods."""

    _API_VERSION = 1
    """:obj:`int`: Version of the API this ApiBase is made for."""

    _API_PATH = "api/V{version}/".format(version=_API_VERSION)
    """:obj:`str`: Base path of API."""

    DEFAULT_FIELDS = {
        "generic": [
            "adapters",
            "labels",
            "specific_data.data.hostname",
            "specific_data.data.network_interfaces.ips",
            "specific_data.data.last_seen",
        ]
    }
    """:obj:`dict`: Fields to set as default for methods with **fields."""

    @property
    def _obj_route(self):
        """Get the object route."""
        return "devices"
