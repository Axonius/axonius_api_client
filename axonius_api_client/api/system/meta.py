# -*- coding: utf-8 -*-
"""API for working with product metadata."""
from ...tools import calc_gb
from ..api_endpoints import ApiEndpoints
from ..mixins import ModelMixins


class Meta(ModelMixins):
    """API for working with product metadata.

    Examples:
        * Get the about page: :meth:`about`
        * Get the product version: :meth:`version`
        * Get historical data disk usage stats: :meth:`historical_sizes`

    """

    def about(self) -> dict:
        """Get about page metadata.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.meta.about()
            >>> j(data)
            {
              "Build Date": "Fri Oct 2 00:18:27 UTC 2020",
              "Customer ID": "e1d48d82f50a4d2085658fea1a59b979",
              "api_client_version": "4.0",
              "Version": "3.10"
            }

        """
        if not hasattr(self, "_about_data"):
            self._about_data = self._about()
        return self._about_data

    def historical_sizes(self) -> dict:
        """Get disk usage metadata.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.meta.historical_sizes()
            >>> data['disk_free_mb']
            70.93
            >>> data['disk_used_mb']
            122.87
            >>> list(data)
            ['disk_free_mb', 'disk_used_mb', 'historical_sizes_devices', 'historical_sizes_users']

        """
        data = self._historical_sizes()
        data["disk_free_mb"] = calc_gb(value=data["disk_free"], is_kb=False)
        data["disk_used_mb"] = calc_gb(value=data["disk_used"], is_kb=False)
        data["historical_sizes_devices"] = data["entity_sizes"].get("Devices", {})
        data["historical_sizes_users"] = data["entity_sizes"].get("Users", {})
        return data

    @property
    def version(self) -> str:
        """Get the version of Axonius.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> client.meta.version
            '3.10'

        """
        return self.about()["Version"]

    def _about(self) -> dict:
        """Direct API method to get the About page."""
        api_endpoint = ApiEndpoints.system_settings.meta_about
        return api_endpoint.perform_request(http=self.auth.http)

    def _historical_sizes(self) -> dict:
        """Direct API method to get the metadata about disk usage."""
        api_endpoint = ApiEndpoints.system_settings.historical_sizes
        return api_endpoint.perform_request(http=self.auth.http)
