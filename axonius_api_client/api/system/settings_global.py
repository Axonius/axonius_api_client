# -*- coding: utf-8 -*-
"""API for working with System Settings -> Global Settings."""
from .. import json_api
from ..api_endpoints import ApiEndpoints
from .settings_mixins import SettingsMixins


class SettingsGlobal(SettingsMixins):
    """API for working with System Settings -> Global Settings."""

    TITLE: str = "Global Settings"

    def _get(self) -> json_api.system_settings.SystemSettings:
        """Direct API method to get the current system settings."""
        api_endpoint = ApiEndpoints.system_settings.global_get
        return api_endpoint.perform_request(http=self.auth.http)

    def _update(self, new_config: dict) -> json_api.system_settings.SystemSettings:
        """Direct API method to update the system settings.

        Args:
            new_config: new system settings to update
        """
        api_endpoint = ApiEndpoints.system_settings.global_update
        request_obj = api_endpoint.load_request(config=new_config)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def configure_destroy(self, enabled: bool, destroy: bool, reset: bool) -> dict:
        """Enable or disable destroy and factory reset API endpoints.

        Args:
            enabled: enable or disable destroy endpoints
            destroy: enable api/devices/destroy and api/users/destroy endpoints
            reset: enable api/factory_reset endpoint
        """
        return self.update_section(
            section="api_settings",
            enabled=enabled,
            enable_factory_reset=reset,
            enable_destroy=destroy,
            check_unchanged=False,
        )
