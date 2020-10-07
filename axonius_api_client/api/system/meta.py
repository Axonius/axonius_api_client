# -*- coding: utf-8 -*-
"""API for working with product metadata."""

from ...parsers.system import parse_sizes
from ..mixins import ModelMixins
from ..routers import API_VERSION, Router


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

            >>> data = meta.about()
            >>> j(data)
            {
              "Build Date": "Fri Oct 2 00:18:27 UTC 2020",
              "Customer ID": "e1d48d82f50a4d2085658fea1a59b979",
              "api_client_version": "4.0",
              "Version": "3.10"
            }

        """
        if not hasattr(self, "_about_data"):
            data = self._about()
            data["Version"] = self._get_version(about=data)
            self._about_data = data
        return self._about_data

    def historical_sizes(self) -> dict:
        """Get disk usage metadata.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = meta.historical_sizes()
            >>> data['disk_free_mb']
            70.93
            >>> data['disk_used_mb']
            122.87
            >>> list(data)
            ['disk_free_mb', 'disk_used_mb', 'historical_sizes_devices', 'historical_sizes_users']

        """
        return parse_sizes(raw=self._historical_sizes())

    @property
    def version(self) -> str:
        """Get the version of Axonius.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> meta.version
            '3.10'

        """
        about = self.about()
        return about["Version"]

    def _get_version(self, about: dict) -> str:
        """Ensure we have a Version key.

        Args:
            about: raw about data from :meth:`_about`
        """
        version = about.pop("Version", "") or about.pop("Installed Version", "")
        version = version.replace("_", ".")
        return version

    def _about(self) -> dict:
        """Direct API method to get the About page."""
        path = self.router.meta_about
        return self.request(method="get", path=path)

    def _historical_sizes(self) -> dict:
        """Direct API method to get the metadata about disk usage."""
        path = self.router.meta_historical_sizes
        return self.request(method="get", path=path)

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.system
