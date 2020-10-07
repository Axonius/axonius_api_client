# -*- coding: utf-8 -*-
"""API for working with instances."""
import datetime
from typing import List, Optional, Union

from ...exceptions import NotFoundError
from ...parsers.system import parse_instances
from ...tools import dt_days_left, dt_parse
from ..mixins import ModelMixins
from ..routers import API_VERSION, Router


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
            >>> list(data)
            ['connection_data', 'instances']
            >>> len(data["instances"])
            1

        """
        return parse_instances(raw=self._get())

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
        instances = self.get()["instances"]
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
        instances = self.get()["instances"]
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
        instances = self.get()["instances"]
        valid = []
        for instance in instances:
            instance_name = instance["name"]
            valid.append(instance_name)
            if instance_name == name:
                return instance[key] if key else instance

        valid = "\n - " + "\n - ".join(valid)
        raise NotFoundError(f"No instance (node) named {name!r} found, valid: {valid}")

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
        node_id = instance["id"]
        hostname = instance["hostname"]
        self._update(node_id=node_id, node_name=new_name, hostname=hostname)
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
        node_id = self.get_by_name(name=name, key="id")
        self._update(node_id=node_id, node_name=name, hostname=value)
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
        node_id = instance["id"]
        hostname = instance["hostname"]
        self._update(
            node_id=node_id, node_name=name, hostname=hostname, use_as_environment_name=enabled
        )
        return self.get_is_env_name(name=name)

    def get_central_core_mode(self) -> bool:
        """Get a bool that shows if a core is in central core mode.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> client.instances.get_central_core_mode()
            False
        """
        return self.get_central_core_config()["central_core_enabled"]

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
        self._update_central_core(enabled=enabled, delete_backups=None)
        return self.get_central_core_mode()

    def get_core_delete_mode(self) -> bool:
        """Get a bool that shows if a core is in central core mode.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> client.instances.get_core_delete_mode()
            True
        """
        return self.get_central_core_config()["core_delete_backups"]

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
        self._update_central_core(enabled=None, delete_backups=enabled)
        return self.get_core_delete_mode()

    def get_central_core_config(self) -> dict:
        """Get the current central core configuration.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> client.instances.get_central_core_config()
            {'core_delete_backups': False, 'central_core_enabled': False}

        """
        data = self._get_central_core()
        data["core_delete_backups"] = data.pop("delete_backups")
        data["central_core_enabled"] = data.pop("enabled")
        return data

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
        """Perform a restore on a core from a file in an AWS S3 Bucket.

        Args:
            key_name: Name of backup file from central core in [bucket_name] to restore to
                this core
            bucket_name: Name of bucket in S3 to get [key_name] from
                (Overrides ``Global Settings > Amazon S3 Settings > Amazon S3 bucket name``)
            access_key_id: AWS Access Key Id to use to access [bucket_name]
                (Overrides ``Global Settings > Amazon S3 Settings > AWS Access Key Id``)
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

    @property
    def feature_flags(self) -> dict:
        """Get the feature flags for the core."""
        return self._feature_flags()

    @property
    def has_cloud_compliance(self) -> bool:
        """Get the status of cloud compliance module being enabled."""
        return self.feature_flags["config"]["cloud_compliance"]["enabled"]

    @property
    def trial_expiry(self) -> Optional[datetime.datetime]:
        """Get the trial expiration date."""
        expiry = self.feature_flags["config"]["trial_end"]
        return dt_parse(obj=expiry) if expiry else None

    @property
    def trial_days_left(self) -> Optional[int]:
        """Get the number of days left for the trial."""
        return dt_days_left(obj=self.trial_expiry)

    @property
    def license_expiry(self) -> Optional[datetime.datetime]:
        """Get the license expiration date."""
        expiry = self.feature_flags["config"]["expiry_date"]
        return dt_parse(obj=expiry) if expiry else None

    @property
    def license_days_left(self) -> Optional[int]:
        """Get the number of days left for the license."""
        return dt_days_left(obj=self.license_expiry)

    def _get(self) -> dict:
        """Direct API method to get instances."""
        return self.request(method="get", path=self.router.root)

    def _delete(self, node_id: str):  # pragma: no cover
        """Direct API method to delete an instance.

        Notes:
            Untested!

        Args:
            node_id: node id of instance
        """
        data = {"nodeIds": node_id}
        path = self.router.root
        return self.request(method="delete", path=path, json=data)

    def _update(self, node_id: str, node_name: str, hostname: str, **kwargs) -> dict:
        """Direct API method to update an instance.

        Args:
            node_id: node id of instance
            node_name: node name of instance
            hostname: hostname of instance
            **kwargs: instance metadata configuration
        """
        data = {"nodeIds": node_id, "node_name": node_name, "hostname": hostname, **kwargs}
        path = self.router.root
        return self.request(method="post", path=path, json=data)

    def _get_central_core(self) -> dict:
        """Direct API method to get the current central core configuration."""
        path = self.router.central_core
        response = self.request(method="get", path=path)
        return response

    def _update_central_core(self, enabled: bool, delete_backups: bool) -> dict:
        """Direct API method to set the current central core configuration.

        Args:
            enabled: enable/disable central core mode (ignored if not True/False)
            delete_backups: enable/disable deletion of backups on a core after resture
                (ignored if not True/False)
        """
        data = {"enabled": enabled, "delete_backups": delete_backups}
        path = self.router.central_core
        response = self.request(method="post", path=path, json=data)
        return response

    def _restore(self, restore_type: str, restore_opts: dict) -> dict:  # pragma: no cover
        """Direct API method to perform a central core restore operation.

        Args:
            restore_type: currently only AWS supported?
            restore_opts: options specific to restore_type
        """
        data = {}
        data["restore_type"] = restore_type
        data.update(restore_opts)

        path = self.router.central_core_restore
        response = self.request(method="post", path=path, json=data, response_timeout=3600)
        return response

    def _feature_flags(self) -> dict:
        """Direct API method to get the feature flags for the core."""
        path = self.router.feature_flags
        response = self.request(method="get", path=path)
        return response

    @property
    def router(self) -> Router:
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        return API_VERSION.instances
