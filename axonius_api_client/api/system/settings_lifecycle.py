# -*- coding: utf-8 -*-
"""API for working with System Settings -> Lifecycle Settings."""
from .. import json_api
from ..api_endpoints import ApiEndpoints
from .settings_mixins import SettingsMixins


class SettingsLifecycle(SettingsMixins):
    """API for working with System Settings -> Lifecycle Settings."""

    TITLE: str = "Lifecycle Settings"

    def _get(self) -> json_api.system_settings.SystemSettings:
        """Direct API method to get the current system settings."""
        api_endpoint = ApiEndpoints.system_settings.lifecycle_get
        return api_endpoint.perform_request(http=self.auth.http)

    def _update(self, new_config: dict) -> json_api.system_settings.SystemSettings:
        """Direct API method to update the system settings.

        Args:
            new_config: new system settings to update
        """
        api_endpoint = ApiEndpoints.system_settings.lifecycle_update
        request_obj = api_endpoint.load_request(config=new_config)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)
