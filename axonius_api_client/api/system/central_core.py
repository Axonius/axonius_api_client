# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from typing import Optional

from ..mixins import ChildMixins


class CentralCore(ChildMixins):
    """Child API model for working with instance metadata."""

    def get(self) -> dict:
        """Get the current central core configuration."""
        return self._get()

    def update(self, enabled: bool, delete_backups: bool) -> dict:
        """Update the current central core configuration."""
        return self._update(enabled=enabled, delete_backups=delete_backups)

    def restore_from_aws_s3(
        self,
        key_name: str,
        bucket_name: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        preshared_key: Optional[str] = None,
        allow_re_restore: bool = False,
        delete_backups: bool = False,
    ) -> dict:
        """Perform a restore from a file object in an AWS S3 Bucket."""
        restore_opts = {}
        restore_opts["key_name"] = key_name
        restore_opts["allow_re_restore"] = allow_re_restore

        if delete_backups is not None:
            restore_opts["delete_backups"] = delete_backups

        if bucket_name is not None:
            restore_opts["bucket_name"] = bucket_name

        if access_key_id is not None:
            restore_opts["access_key_id"] = access_key_id

        if secret_access_key is not None:
            restore_opts["secret_access_key"] = secret_access_key

        if preshared_key is not None:
            restore_opts["preshared_key"] = preshared_key

        return self._restore(restore_type="aws", restore_opts=restore_opts)

    def _get(self) -> dict:
        """Get the current central core configuration."""
        path = self.router.central_core
        response = self.request(method="get", path=path)
        return response

    def _update(self, enabled: bool, delete_backups: bool) -> dict:
        """Set the current central core configuration."""
        data = {"enabled": enabled, "delete_backups": delete_backups}
        path = self.router.central_core
        response = self.request(method="post", path=path, json=data)
        return response

    def _restore(self, restore_type: str, restore_opts: dict) -> dict:
        """Perform a central core restore operation."""
        data = {}
        data["restore_type"] = restore_type
        data.update(restore_opts)

        path = self.router.central_core_restore
        response = self.request(
            method="post", path=path, json=data, response_timeout=3600
        )
        return response
