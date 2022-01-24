# -*- coding: utf-8 -*-
"""API for working with System Settings -> Global Settings."""
import pathlib
from typing import Union

from .. import json_api
from ..api_endpoints import ApiEndpoints
from .settings_mixins import SettingsMixins
from ...tools import path_read


class SettingsGlobal(SettingsMixins):
    """API for working with System Settings -> Global Settings."""

    TITLE: str = "Global Settings"

    @property
    def title(self) -> str:
        return self.TITLE

    @property
    def plugin_name(self) -> str:
        return "core"

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

    # def upload_cert(self, contents, name):
    # def upload_cert_path(self, path, ....):

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

    def ssl_update_path(
        self,
        cert_file_path: Union[str, pathlib.Path],
        key_file_path: Union[str, pathlib.Path],
        **kwargs
    ) -> bool:
        cert_file_path, cert_file_contents = path_read(obj=cert_file_path, binary=True)
        kwargs["cert_file_name"] = cert_file_path.name
        kwargs["cert_file_contents"] = cert_file_contents

        key_file_path, key_file_contents = path_read(obj=key_file_path, binary=True)
        kwargs["key_file_name"] = key_file_path.name
        kwargs["key_file_contents"] = key_file_contents

        return self.ssl_update(**kwargs)

    def ssl_update(
        self,
        cert_file_contents: Union[str, bytes],
        cert_file_name: str,
        key_file_contents: Union[str, bytes],
        key_file_name: str,
        hostname: str,
        enabled: bool,
        passphrase: str = "",
    ) -> bool:
        cert_file = self._file_upload(
            field_name="cert_file",
            file_name=cert_file_name,
            file_content=cert_file_contents,
            file_content_type="application/x-x509-ca-cert",
        ).to_dict_file_spec()
        key_file = self._file_upload(
            field_name="private_key",
            file_name=key_file_name,
            file_content=key_file_contents,
            file_content_type="application/octet-stream",
        ).to_dict_file_spec()
        return self._ssl_update(
            hostname=hostname,
            passphrase=passphrase,
            enabled=enabled,
            cert_file=cert_file,
            private_key=key_file,
        )

    def _ssl_update(self, **kwargs) -> bool:
        api_endpoint = ApiEndpoints.system_settings.ssl_update
        request_obj = api_endpoint.load_request(**kwargs)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def ssl_certificate_details(self) -> json_api.system_settings.SSLCertificate:
        return self._ssl_certificate_details()

    def _ssl_certificate_details(self) -> json_api.system_settings.SSLCertificate:
        api_endpoint = ApiEndpoints.system_settings.ssl_certificate_details
        return api_endpoint.perform_request(http=self.auth.http)
