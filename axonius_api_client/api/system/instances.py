# -*- coding: utf-8 -*-
"""API for working with instances."""
import datetime
import math
import pathlib
from typing import List, Optional, Union

import cachetools
import requests

from ...exceptions import FeatureNotEnabledError, NotFoundError
from ...parsers.tables import tablize
from ...tools import is_url, path_read
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ModelMixins

FEATURE_FLAGS_CACHE = cachetools.TTLCache(maxsize=1, ttl=10)
TUNNEL_MODEL = json_api.instances.Tunnel


class Instances(ModelMixins):
    """API for working with instances.

    Examples:
        * Get all instances: :meth:`get`
        * Get the core instance: :meth:`get_core`
        * Get all collector instances: :meth:`get_collectors`
        * Get an instance by name: :meth:`get_by_name`
        * Set the name of an instance: :meth:`set_name`
        * Get the hostname of an instance: :meth:`get_hostname`
        * Set the hostname of an instance: :meth:`get_hostname`
        * Get the setting for is environment name of an instance: :meth:`get_is_env_name`
        * Set the setting for is environment name of an instance: :meth:`set_is_env_name`
        * Get the central core mode: :meth:`get_central_core_mode`
        * Set the central core mode: :meth:`get_central_core_mode`
        * Get the core delete backups mode: :meth:`get_core_delete_mode`
        * Set the core delete backups mode: :meth:`set_core_delete_mode`
        * Get the central core config: :meth:`get_central_core_config`
        * Perform a restore on a core from a file in an AWS S3 Bucket: :meth:`restore_from_aws_s3`

    Notes:
        Certain functionality is not yet exposed, please submit a feature request via
        support@axonius.com if you would like to:

        * Deactivate an instance
        * Connect an instance
        * Tag an instance
    """

    def get(self) -> dict:
        """Get metadata about all instances.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.instances.get()
            >>> len(data)
            1

        """
        return [x.to_dict() for x in self._get()]

    def get_core(self, key: Optional[str] = None) -> Union[dict, Union[str, bool, int, float]]:
        """Get the core instance.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> instance = client.instances.get_core()
            >>> instance['node_name']
            'Master'
            >>> instance['cpu_usage']
            39
            >>> instance['data_disk_free_space']
            74431500
            >>> instance['hostname']
            'builds-vm-jim-pre-3-10-1601596999-000'
            >>> instance['ips']
            ['10.20.0.61']
            >>> instance['data_disk_free_space_percent']
            36.62
            >>> instance['memory_free_space_percent']
            1.46
            >>> instance['swap_free_space_percent']
            0.0

        Args:
            key: key to return or just return whole object

        """
        instances = self.get()
        for instance in instances:
            if instance["is_master"]:
                return instance[key] if key else instance

    def get_collectors(self) -> List[dict]:
        """Get the collector instances.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> collectors = client.instances.get_collectors()
            >>> len(collectors)
            0

        """
        instances = self.get()
        return [x for x in instances if not x.get("is_master")]

    def get_by_name(
        self, name: str, key: Optional[str] = None
    ) -> Union[dict, Union[str, bool, int, float]]:
        """Get an instance by name.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> instance = client.instances.get_by_name("Master")
            >>> instance['cpu_usage']
            39
            >>> instance['data_disk_free_space']
            74431500
            >>> instance['hostname']
            'builds-vm-jim-pre-3-10-1601596999-000'
            >>> instance['ips']
            ['10.20.0.61']
            >>> instance['data_disk_free_space_percent']
            36.62
            >>> instance['memory_free_space_percent']
            1.46
            >>> instance['swap_free_space_percent']
            0.0

        Args:
            name: name of instance
            key: key to return or just return whole object
        """
        instances = self.get()
        valid = []
        for instance in instances:
            instance_name = instance["name"]
            valid.append(instance_name)
            if instance_name == name:
                return instance[key] if key else instance

        valid = "\n - " + "\n - ".join(valid)
        raise NotFoundError(f"No instance (node) named {name!r} found, valid: {valid}")

    def get_by_name_id_core(self, value: Optional[str] = None, serial: bool = True) -> dict:
        """Pass."""
        data = None
        instances = self._get()

        for instance in instances:
            if not value and instance.is_master:
                data = instance
                break

            if instance.name == value or instance.id == value:
                data = instance
                break

        if not data:
            valid = [f"Name: {x.name}, ID: {x.id}" for x in instances]
            valid = "\n - " + "\n - ".join(valid)
            raise NotFoundError(f"No instance with ID or name of {value!r} found, valid:{valid}")

        if serial:
            data = data.to_dict()
            data = {k: str(v) if isinstance(v, datetime.datetime) else v for k, v in data.items()}
        return data

    def check_tunnel_feature(self, feature_error: bool = True) -> bool:
        """Pass."""
        enabled = self.has_saas_enabled
        if not enabled:
            if feature_error:
                raise FeatureNotEnabledError(name="enable_saas")
        return enabled

    def get_tunnels(self, feature_error: bool = True) -> List[TUNNEL_MODEL]:
        """Pass."""
        enabled = self.check_tunnel_feature(feature_error=feature_error)
        if enabled:
            tunnels = self._get_tunnels()
            if isinstance(tunnels, (list, tuple)):
                return tunnels
        return []

    def get_tunnel(
        self,
        value: Optional[str] = None,
        return_id: bool = False,
        feature_error: bool = True,
    ) -> Optional[Union[TUNNEL_MODEL, str]]:
        """Pass."""
        if isinstance(value, TUNNEL_MODEL):
            return value.id if return_id else value

        if isinstance(value, str) and value.strip():
            tunnels = self.get_tunnels(feature_error=feature_error)
            for tunnel in tunnels:
                if value in [tunnel.id, tunnel.name]:
                    return tunnel.id if return_id else tunnel

            err = f"No tunnel found with ID or Name of {value!r} out of {len(tunnels)} tunnels"
            err_table = tablize(value=[x.to_tablize() for x in tunnels], err=err)
            raise NotFoundError(err_table)
        return None

    def get_tunnel_default(
        self, return_id: bool = False, feature_error: bool = True
    ) -> Optional[Union[TUNNEL_MODEL, str]]:
        """Pass."""
        tunnels = self.get_tunnels(feature_error=feature_error)
        for tunnel in tunnels:
            if tunnel.default is True:
                return tunnel.id if return_id else tunnel
        return None

    def set_name(self, name: str, new_name: str) -> str:
        """Set the name of an instance.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Get the current name

            >>> orig_value = client.instances.get_core(key='name')
            >>> orig_value
            'Master'

            Set a new name

            >>> new_value = client.instances.set_name(name=orig_value, new_name='Temp')
            >>> new_value
            'Temp'

            Revert back to the original name

            >>> reset_value = client.instances.set_name(name=new_value, new_name=orig_value)
            >>> reset_value
            'Master'

        Args:
            name: name of instance
            new_name: new name to set on instance
        """
        instance = self.get_by_name(name=name)
        self._update_attrs(
            node_id=instance["id"],
            node_name=new_name,
            hostname=instance["hostname"],
            use_as_environment_name=instance["use_as_environment_name"],
        )
        return self.get_by_name(name=new_name, key="name")

    def get_hostname(self, name: str) -> str:
        """Get the host name of an instance.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Get the hostname

            >>> hostname = client.instances.get_hostname(name='Master')
            >>> hostname
            'builds-vm-jim-pre-3-10-1601596999-000'

        Args:
            name: name of instance
            value: new hostname to set on instance
        """
        return self.get_by_name(name=name, key="hostname")

    def set_hostname(self, name: str, value: str) -> str:
        """Set the hostname of an instance.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Get the current hostname

            >>> orig_value = client.instances.get_hostname(name='Master')
            >>> orig_value
            'builds-vm-jim-pre-3-10-1601596999-000'

            Set a new hostname

            >>> new_value = client.instances.set_hostname(name='Master', value="hostname")
            >>> new_value
            "hostname"

            Revert to the old hostname

            >>> reset_value = client.instances.set_hostname(name='Master', value=orig_value)
            >>> reset_value
            'builds-vm-jim-pre-3-10-1601596999-000'

        Args:
            name: name of instance
            value: new hostname to set on instance
        """
        instance = self.get_by_name(name=name)
        self._update_attrs(
            node_id=instance["id"],
            node_name=instance["node_name"],
            hostname=value,
            use_as_environment_name=instance["use_as_environment_name"],
        )
        return self.get_hostname(name=name)

    def get_is_env_name(self, name: str) -> bool:
        """See if an instance name is being used for the environment name.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> client.instances.get_is_env_name(name='Master')
            False

        Notes:
            Environment name is the name shown in the banner at the bottom of the GUI.

        Args:
            name: name of instance
        """
        return self.get_by_name(name=name, key="use_as_environment_name")

    def set_is_env_name(self, name: str, enabled: bool) -> bool:
        """Set if an instance name is being used for the environment name.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Enable an instance name as the environment name

            >>> client.instances.set_is_env_name(name='Master', enabled=True)
            True

            Disable an instance name as the environment name

            >>> client.instances.set_is_env_name(name='Master', enabled=False)
            False

        Notes:
            Environment name is the name shown in the banner at the bottom of the GUI.

        Args:
            name: name of instance
            enabled: enable/disable instance name as the environment name
        """
        instance = self.get_by_name(name=name)
        self._update_attrs(
            node_id=instance["id"],
            node_name=instance["node_name"],
            hostname=instance["hostname"],
            use_as_environment_name=enabled,
        )
        return self.get_is_env_name(name=name)

    def get_central_core_mode(self) -> bool:
        """Get a bool that shows if a core is in central core mode.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> client.instances.get_central_core_mode()
            False
        """
        data = self.get_central_core_config()
        return data["enabled"]

    def set_central_core_mode(self, enabled: bool) -> bool:
        """Convert a normal core into a central core.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Enable central core mode on a core

            >>> client.instances.set_central_core_mode(enabled=True)
            True

            Disable central core mode on a core

            >>> client.instances.set_central_core_mode(enabled=False)
            False

        Args:
            enabled: enable/disable central core mode
        """
        data = self.get_central_core_config()
        self._update_central_core_config(enabled=enabled, delete_backups=data["delete_backups"])
        return self.get_central_core_mode()

    def get_core_delete_mode(self) -> bool:
        """Get a bool that shows if a core is in central core mode.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> client.instances.get_core_delete_mode()
            True
        """
        data = self.get_central_core_config()
        return data["delete_backups"]

    def set_core_delete_mode(self, enabled: bool) -> bool:
        """Configure a normal core to delete backups after they have been restored.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Set backups to delete after restore

            >>> client.instances.set_core_delete_mode(enabled=True)
            True

            Set backups to NOT delete after restore

            >>> client.instances.set_core_delete_mode(enabled=False)
            False

        Args:
            enabled: enable/disable deletion of backups after they have been restored by a core
        """
        data = self.get_central_core_config()
        self._update_central_core_config(enabled=data["enabled"], delete_backups=enabled)
        return self.get_core_delete_mode()

    def factory_reset(
        self, reset: bool = False
    ) -> json_api.instances.FactoryReset:  # pragma: no cover
        """Perform a factory reset on an instance.

        Notes:
            Can not run in test suite!

        Args:
            reset: actually do it... be careful!
        """
        return self._factory_reset(approve_not_recoverable_action=reset)

    def get_central_core_config(self) -> dict:
        """Get the current central core configuration.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> client.instances.get_central_core_config()
            {'core_delete_backups': False, 'central_core_enabled': False}

        """
        data = self._get_central_core_config()
        return data.to_dict()["config"]

    def restore_from_aws_s3(
        self,
        key_name: str,
        bucket_name: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        preshared_key: Optional[str] = None,
        allow_re_restore: Optional[bool] = None,
        delete_backups: Optional[bool] = None,
    ) -> dict:  # pragma: no cover
        """Perform a restore on a core from a file in an AWS S3 Bucket.

        Notes:
            Can not run in test suite!

        Args:
            key_name: Name of backup file from central core in [bucket_name] to restore to
                this core
            bucket_name: Name of bucket in S3 to get [key_name] from
                (Overrides ``Global Settings > Amazon S3 Settings > Amazon S3 bucket name``)
            access_key_id: AWS Access Key ID to use to access [bucket_name]
                (Overrides ``Global Settings > Amazon S3 Settings > AWS Access Key ID``)
            secret_access_key: AWS Secret Access Key to use to access [bucket_name]
                (Overrides ``Global Settings > Amazon S3 Settings > AWS Secret Access Key``)
            preshared_key: Password to use to decrypt [key_name]
                (Overrides: ``Global Settings > Amazon S3 Settings > Backup encryption passphrase``)
            allow_re_restore: Restore [key_name] even if it has already been restored
            delete_backups: Delete [key_name] from [bucket_name] after restore has finished
                (Overrides the current value of :meth:`get_core_delete_mode`)
        """
        restore_opts = {}
        restore_opts["key_name"] = key_name
        restore_opts["allow_re_restore"] = allow_re_restore
        restore_opts["delete_backups"] = delete_backups
        restore_opts["bucket_name"] = bucket_name
        restore_opts["access_key_id"] = access_key_id
        restore_opts["secret_access_key"] = secret_access_key
        restore_opts["preshared_key"] = preshared_key
        response = self._restore_aws(**restore_opts)
        return response.to_dict()

    @property
    def api_version(self) -> str:
        """Pass."""
        return self._get_api_version().value

    @property
    def api_versions(self) -> List[str]:
        """Pass."""
        return [x.value for x in self._get_api_versions()]

    @property
    @cachetools.cached(cache=FEATURE_FLAGS_CACHE)
    def feature_flags(self) -> json_api.system_settings.FeatureFlags:
        """Get the feature flags for the core."""
        return self._feature_flags()

    @property
    def has_saas_enabled(self) -> bool:
        """Get the status of SAAS & tunnel support being enabled."""
        return self.feature_flags.saas_enabled

    @property
    def has_cloud_compliance(self) -> bool:
        """Get the status of cloud compliance module being enabled."""
        return self.feature_flags.has_cloud_compliance

    @property
    def trial_expiry(self) -> Optional[datetime.datetime]:
        """Get the trial expiration date."""
        return self.feature_flags.trial_expiry_dt

    @property
    def trial_days_left(self) -> Optional[int]:
        """Get the number of days left for the trial."""
        return self.feature_flags.trial_expiry_in_days

    @property
    def license_expiry(self) -> Optional[datetime.datetime]:
        """Get the license expiration date."""
        return self.feature_flags.license_expiry_dt

    @property
    def license_days_left(self) -> Optional[int]:
        """Get the number of days left for the license."""
        return self.feature_flags.license_expiry_in_days

    def admin_script_upload(self, file_name: str, file_content: Union[str, bytes]) -> dict:
        """Upload an admin script and execute it.

        Args:
            file_name: name to give uploaded script file
            file_content: content to upload
        """
        response = self._admin_script_upload(file_name=file_name, file_content=file_content)
        response["execute_result"] = self._admin_script_execute(uuid=response["file_uuid"])
        return response

    def admin_script_upload_path(
        self, path: Union[str, pathlib.Path], path_verify: bool = True, **kwargs
    ) -> dict:
        """Upload an admin script from a file or URL and execute it.

        Args:
            path: URL or path to file of script to upload and execute
            **kwargs: passed to :meth:`upload_script`
        """
        if is_url(value=path):
            from ...projects.url_parser import UrlParser

            parser = UrlParser(url=path)
            path_part = pathlib.Path(parser.parsed.path)
            file_name = path_part.name
            request: dict = {}
            request["url"] = path
            request["verify"] = path_verify
            response = requests.get(**request)
            file_content = response.content
        else:
            path_part, file_content = path_read(obj=path, binary=True, is_json=False)
            file_name = path_part.name

        kwargs.setdefault("file_name", file_name)
        kwargs["file_content"] = file_content
        return self.admin_script_upload(**kwargs)

    def _get(self) -> List[json_api.instances.Instance]:
        """Direct API method to get instances."""
        api_endpoint = ApiEndpoints.instances.get
        return api_endpoint.perform_request(http=self.auth.http)

    def _factory_reset(
        self, approve_not_recoverable_action: bool = False
    ) -> json_api.instances.FactoryReset:  # pragma: no cover
        """Direct API method to do a factory reset on an instance.

        Notes:
            Can not run in test suite!

        Args:
            approve_not_recoverable_action: actually do it... be careful!
        """
        api_endpoint = ApiEndpoints.instances.factory_reset
        request_obj = api_endpoint.load_request(
            approve_not_recoverable_action=approve_not_recoverable_action
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _delete(self, node_id: str) -> str:  # pragma: no cover
        """Direct API method to delete an instance.

        Notes:
            Can not run in test suite!

        Args:
            node_id: node id of instance
        """
        api_endpoint = ApiEndpoints.instances.delete
        request_obj = api_endpoint.load_request(nodeIds=[node_id])
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _update_attrs(
        self, node_id: str, node_name: str, hostname: str, use_as_environment_name: bool
    ) -> str:
        """Direct API method to update an instance.

        Args:
            node_id: node id of instance
            node_name: node name of instance
            hostname: hostname of instance
            use_as_environment_name: instance name is being used for the environment name
        """
        api_endpoint = ApiEndpoints.instances.update_attrs
        request_obj = api_endpoint.load_request(
            nodeIds=node_id,
            node_name=node_name,
            hostname=hostname,
            use_as_environment_name=use_as_environment_name,
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _update_active(self, node_id: str, status: bool) -> str:  # pragma: no cover
        """Direct API method to update an instance.

        Notes:
            Can not run in test suite!

        Args:
            node_id: node id of instance
            status: enabled or disabled an instance
        """
        api_endpoint = ApiEndpoints.instances.update_active
        request_obj = api_endpoint.load_request(nodeIds=node_id, status=status)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _get_central_core_config(self) -> json_api.system_settings.SystemSettings:
        """Direct API method to get the current central core configuration."""
        api_endpoint = ApiEndpoints.central_core.settings_get
        return api_endpoint.perform_request(http=self.auth.http)

    def _update_central_core_config(
        self, enabled: bool, delete_backups: bool
    ) -> json_api.system_settings.SystemSettings:
        """Direct API method to set the current central core configuration.

        Args:
            enabled: enable/disable central core mode (ignored if not True/False)
            delete_backups: enable/disable deletion of backups on a core after resture
                (ignored if not True/False)
        """
        api_endpoint = ApiEndpoints.central_core.settings_update
        request_obj = api_endpoint.load_request(enabled=enabled, delete_backups=delete_backups)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _restore_aws(
        self,
        key_name: str,
        bucket_name: Optional[str] = None,
        preshared_key: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        delete_backups: Optional[bool] = None,
        allow_re_restore: Optional[bool] = None,
    ) -> json_api.central_core.CentralCoreRestore:  # pragma: no cover
        """Direct API method to perform a central core restore operation.

        Notes:
            Can not run in test suite!

        Args:
            restore_type: currently only AWS supported?
            additional_data: options specific to restore_type
        """
        api_endpoint = ApiEndpoints.central_core.restore_aws
        request_obj = api_endpoint.load_request(
            additional_data={
                "key_name": key_name,
                "bucket_name": bucket_name,
                "preshared_key": preshared_key,
                "access_key_id": access_key_id,
                "secret_access_key": secret_access_key,
                "delete_backups": delete_backups,
                "allow_re_restore": allow_re_restore,
            }
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _feature_flags(self) -> json_api.system_settings.FeatureFlags:
        """Direct API method to get the feature flags for the core."""
        api_endpoint = ApiEndpoints.system_settings.feature_flags_get
        return api_endpoint.perform_request(http=self.auth.http)

    def _admin_script_upload(
        self, file_name: str, file_content: Union[bytes, str], chunk_size: int = 1024 * 1024 * 100
    ) -> dict:
        """Upload an admin script."""
        file_size = len(file_content)
        chunk_count = math.ceil(file_size / chunk_size)
        chunk_current = 0

        start_endpoint = ApiEndpoints.instances.admin_script_upload_start
        headers = {"Upload-Length": f"{file_size}"}
        http_args = {"data": file_name, "headers": headers}
        file_uuid = start_endpoint.perform_request(http=self.auth.http, http_args=http_args)

        chunk_responses = []
        chunk_endpoint = ApiEndpoints.instances.admin_script_upload_chunk
        while chunk_current < chunk_count:
            chunk_start = chunk_current * chunk_size
            chunk_end = chunk_start + chunk_size
            chunk = file_content[chunk_start:chunk_end]

            headers = {
                "Content-Type": "application/offset+octet-stream",
                "Upload-Length": f"{file_size}",
                "Upload-Name": f"{file_name}",
                "Upload-Offset": f"{chunk_start}",
            }
            http_args = {"data": chunk, "headers": headers}
            chunk_response = chunk_endpoint.perform_request(
                http=self.auth.http, http_args=http_args, uuid=file_uuid
            )
            chunk_responses.append({"uuid": chunk_response, "start": chunk_start, "end": chunk_end})
            chunk_current += 1

        return {
            "file_name": file_name,
            "file_uuid": file_uuid,
            "file_size": file_size,
            "chunks": chunk_responses,
            "chunk_count": chunk_count,
            "chunk_size": chunk_size,
        }

    def _admin_script_execute(self, uuid: str) -> str:
        """Upload a script file."""
        api_endpoint = ApiEndpoints.instances.admin_script_execute

        response = api_endpoint.perform_request(http=self.auth.http, uuid=uuid)
        return response

    def _get_api_version(self) -> json_api.generic.StrValueSchema:
        """Pass."""
        return ApiEndpoints.instances.get_api_version.perform_request(http=self.auth.http)

    def _get_api_versions(self) -> json_api.generic.StrValueSchema:
        return ApiEndpoints.instances.get_api_versions.perform_request(http=self.auth.http)

    def _get_tunnels(self) -> Union[str, List[TUNNEL_MODEL]]:
        return ApiEndpoints.instances.get_tunnels.perform_request(http=self.auth.http)
