# -*- coding: utf-8 -*-
"""API for working with instance metadata."""
import math

from ..mixins import ModelMixins
from ..routers import API_VERSION, Router


class Meta(ModelMixins):
    """Child API model for working with instance metadata."""

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.system

    def about(self) -> dict:
        """Get about page metadata.

        Returns:
            :obj:`dict`: about page metadata
        """
        if not hasattr(self, "_about_data"):
            data = self._about()
            data["Version"] = self._get_version(about=data)
            self._about_data = data
        return self._about_data

    def historical_sizes(self) -> dict:
        """Get disk usage metadata.

        Returns:
            :obj:`dict`: disk usage metadata
        """
        return parse_sizes(self._historical_sizes())

    def _get_version(self, about: dict) -> str:
        """Pass."""
        version = about.pop("Version", "") or about.pop("Installed Version", "")
        version = version.replace("_", ".")
        return version

    @property
    def version(self) -> str:
        """Get the version of Axonius."""
        about = self.about()
        return about["Version"]

    def _about(self) -> dict:
        """Direct API method to get the About page.

        Returns:
            :obj:`dict`: about page metadata
        """
        path = self.router.meta_about
        return self.request(method="get", path=path)

    def _historical_sizes(self) -> dict:
        """Direct API method to get the metadata about disk usage.

        Returns:
            :obj:`dict`: disk usage metadata
        """
        path = self.router.meta_historical_sizes
        return self.request(method="get", path=path)


def parse_sizes(raw: dict) -> dict:
    """Pass."""
    parsed = {}
    parsed["disk_free_mb"] = math.floor(raw["disk_free"] / 1024 / 1024)
    parsed["disk_used_mb"] = math.ceil(raw["disk_used"] / 1024 / 1024)
    parsed["historical_sizes_devices"] = raw["entity_sizes"].get("Devices", {})
    parsed["historical_sizes_users"] = raw["entity_sizes"].get("Users", {})
    return parsed
