# -*- coding: utf-8 -*-
"""API for working with product metadata."""
from typing import Optional

from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ModelMixins


class RemoteSupport(ModelMixins):
    """API for working with configuring remote support system settings.

    Examples:
        NATCH

    """

    def get(self) -> json_api.remote_support.RemoteSupport:
        """Pass."""
        return self._get()

    def configure(
        self, enable: bool, temp_hours: Optional[int] = None
    ) -> json_api.remote_support.RemoteSupport:
        """Configure remote support.

        Args:
            enable: turn "Remote Support" on or off
            temp_hours: if enable is true, only enable for N hours

        """

        def stop_temp():
            if current_data.enabled_temporarily:
                self._stop_temporary()

        current_data = self.get()

        if enable and temp_hours:
            self._update_permanent(provision=False)
            self._start_temporary(hours=temp_hours)
        elif enable:
            stop_temp()
            self._update_permanent(provision=True)
        elif not enable:
            stop_temp()
            self._update_permanent(provision=False)
        return self.get()

    def configure_analytics(self, enable: bool) -> json_api.remote_support.RemoteSupport:
        """Configure Anonymized Analytics.

        Args:
            enable: turn "Remote Support > Anonymized Analytics" on or off

        """
        self._update_analytics(analytics=enable)
        return self.get()

    def configure_remote_access(self, enable: bool) -> json_api.remote_support.RemoteSupport:
        """Configure Remote Access.

        Args:
            enable: turn "Remote Support > Remote Access" on or off

        """
        self._update_troubleshooting(troubleshooting=enable)
        return self.get()

    def _get(self) -> json_api.remote_support.RemoteSupport:
        """Direct API method to get the properties for remote support."""
        api_endpoint = ApiEndpoints.remote_support.get
        return api_endpoint.perform_request(http=self.auth.http)

    def _update_permanent(
        self,
        provision: bool,
    ) -> str:
        """Direct API method to update the properties for remote support."""
        api_endpoint = ApiEndpoints.remote_support.permanent_update
        request_obj = api_endpoint.load_request(provision=provision)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _update_analytics(
        self,
        analytics: bool,
    ) -> str:
        """Direct API method to update the properties for remote support."""
        api_endpoint = ApiEndpoints.remote_support.analytics_update
        request_obj = api_endpoint.load_request(analytics=analytics)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _update_troubleshooting(
        self,
        troubleshooting: bool,
    ) -> str:
        """Direct API method to update the properties for remote support."""
        api_endpoint = ApiEndpoints.remote_support.troubleshooting_update
        request_obj = api_endpoint.load_request(troubleshooting=troubleshooting)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _start_temporary(self, hours: int) -> json_api.remote_support.UpdateTemporaryResponse:
        """Direct API method to enable temporary remote support."""
        api_endpoint = ApiEndpoints.remote_support.temporary_enable
        request_obj = api_endpoint.load_request(duration=hours)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _stop_temporary(self) -> str:
        """Direct API method to stop temporary remote support."""
        api_endpoint = ApiEndpoints.remote_support.temporary_disable
        return api_endpoint.perform_request(http=self.auth.http)
