# -*- coding: utf-8 -*-
"""API for working with central core configuration ``[DEPRECATED]``."""
from typing import Optional

from ..mixins import ModelMixins
from ..routers import API_VERSION, Router


class CentralCore(ModelMixins):  # pragma: no cover
    """API for working with central core configuration ``[DEPRECATED]``.

    Warning:
        This object is deprecated. Use :obj:`axonius_api_client.api.system.instances.Instances`
    """

    def get(self) -> dict:  # pragma: no cover
        """Get the current central core configuration ``[DEPRECATED]``."""
        return self._get()

    def update(self, enabled: bool, delete_backups: bool) -> dict:  # pragma: no cover
        """Update the current central core configuration ``[DEPRECATED]``."""
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
    ) -> dict:  # pragma: no cover
        """Perform a restore on a core from a file in an AWS S3 Bucket ``[DEPRECATED]``."""
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

    def _get(self) -> dict:  # pragma: no cover
        """Get the current central core configuration ``[DEPRECATED]``."""
        path = self.router.central_core
        response = self.request(method="get", path=path)
        return response

    def _update(self, enabled: bool, delete_backups: bool) -> dict:  # pragma: no cover
        """Set the current central core configuration ``[DEPRECATED]``."""
        data = {"enabled": enabled, "delete_backups": delete_backups}
        path = self.router.central_core
        response = self.request(method="post", path=path, json=data)
        return response

    def _restore(self, restore_type: str, restore_opts: dict) -> dict:  # pragma: no cover
        """Perform a central core restore operation ``[DEPRECATED]``."""
        data = {}
        data["restore_type"] = restore_type
        data.update(restore_opts)

        path = self.router.central_core_restore
        response = self.request(method="post", path=path, json=data, response_timeout=3600)
        return response

    @property
    def router(self) -> Router:  # pragma: no cover
        """Router for this API model ``[DEPRECATED]``."""
        return API_VERSION.system
