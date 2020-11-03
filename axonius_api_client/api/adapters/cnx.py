# -*- coding: utf-8 -*-
"""API for working with adapter connections."""
import time
from typing import List, Optional, Union

from ...constants.adapters import CNX_GONE, CNX_RETRY, CNX_SANE_DEFAULTS
from ...exceptions import (
    CnxAddError,
    CnxGoneError,
    CnxTestError,
    CnxUpdateError,
    ConfigInvalidValue,
    ConfigRequired,
    NotFoundError,
)
from ...parsers.config import (
    config_build,
    config_default,
    config_empty,
    config_info,
    config_required,
    config_unchanged,
    config_unknown,
)
from ...parsers.tables import tablize_cnxs, tablize_schemas
from ...tools import json_load, pathlib
from ..mixins import ChildMixins


class Cnx(ChildMixins):
    """API model for working with adapter connections.

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

        * Add a connection: :meth:`add`
        * Get all connections for an adapter: :meth:`get_by_adapter`
        * Get a connection for an adapter by UUID: :meth:`get_by_uuid`
        * Get a connection for an adapter by connection label: :meth:`get_by_label`
        * Get a connection for an adapter by ID: :meth:`get_by_id`
        * Update a connection for an adapter by ID: :meth:`update_by_id`
        * Delete a connection for an adapter by ID: :meth:`delete_by_id`
        * Test a connections parameters for an adapter without creating the connection: :meth:`test`
        * Work with adapters :obj:`axonius_api_client.api.adapters.adapters.Adapters`

    Notes:
        All methods use the Core instance by default, but you can work with another instance by
        passing the name of the instance to ``adapter_node``.

        Supplying unknown keys/values for configurations will throw an error showing the
        valid keys/values.
    """

    def add(self, adapter_name: str, adapter_node: Optional[str] = None, **kwargs) -> dict:
        """Add a connection to an adapter on a node.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Establish a connection dictionary

            >>> config = dict(
            ...     dc_name="192.168.1.10",
            ...     user="svc_user",
            ...     password="test",
            ...     do_not_fetch_users=False,
            ...     fetch_disabled_users=False,
            ...     fetch_disabled_devices=False,
            ...     is_ad_gc=False,
            ...     connection_label="test label",
            ... )

            Add a connection for an adapter to the Core instance

            >>> cnx = client.adapters.cnx.add(adapter_name="active_directory", **config)

        Args:
            adapter_name: name of adapter
            adapter_node: name of node running adapter
            **kwargs: configuration of new connection

        Raises:
            :exc:`CnxAddError`: when an error happens while adding the connection
        """
        kwargs_config = kwargs.pop("kwargs_config", {})
        kwargs.update(kwargs_config)

        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node)
        cnx_schemas = adapter["schemas"]["cnx"]
        adapter_name = adapter["name"]
        adapter_node_name = adapter["node_name"]
        adapter_name_raw = adapter["name_raw"]
        adapter_node_id = adapter["node_id"]

        source = f"adding connection for adapter {adapter_name!r}"

        new_config = self.build_config(
            cnx_schemas=cnx_schemas,
            new_config=kwargs,
            source=source,
            adapter_name=adapter_name,
            adapter_node=adapter_node_name,
        )

        sane_defaults = self.get_sane_defaults(adapter_name=adapter_name)

        config_default(
            schemas=cnx_schemas,
            new_config=new_config,
            source=source,
            sane_defaults=sane_defaults,
        )

        config_empty(schemas=cnx_schemas, new_config=new_config, source=source)

        config_required(schemas=cnx_schemas, new_config=new_config, source=source)

        result = self._add(
            adapter_name_raw=adapter_name_raw,
            adapter_node_id=adapter_node_id,
            new_config=new_config,
        )

        error_in_status = result.get("status", "") == "error"
        error_empty = bool(result.get("error", ""))

        cnx_new = self.get_by_uuid(
            cnx_uuid=result["id"],
            adapter_name=adapter_name,
            adapter_node=adapter_node,
            retry=CNX_RETRY,
        )

        if any([error_in_status, error_empty]):
            rkw = ["{}: {}".format(k, v) for k, v in result.items()]
            rkw = "\n  " + "\n  ".join(rkw)

            err = f"Connection was added but had a failure connecting:{rkw}"
            exc = CnxAddError(err)

            exc.result = result
            exc.cnx_new = cnx_new
            raise exc

        return cnx_new

    def get_by_adapter(self, adapter_name: str, adapter_node: Optional[str] = None) -> List[dict]:
        """Get all connections of an adapter on a node.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Get all connections for an adapter on the Core instance

            >>> cnxs = client.adapters.cnx.get_by_adapter(adapter_name="active_directory")

        Args:
            adapter_name: name of adapter
            adapter_node: name of node running adapter
        """
        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node)
        cnxs = adapter["cnx"]

        for cnx in cnxs:
            cnx["schemas"] = adapter["schemas"]["cnx"]

        return cnxs

    def get_by_uuid(
        self, cnx_uuid: str, adapter_name: str, adapter_node: Optional[str] = None, **kwargs
    ) -> dict:
        """Get a connection for an adapter on a node by UUID.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Get a single connection by UUID

            >>> cnx = client.adapters.cnx.get_by_uuid(
            ...     cnx_id='5f76735be4557d5cba94237f', adapter_name='aws'
            ... )

        Notes:
            UUID of connections change when a connection configuration is updated,
            the more persistent way to get a connection is :meth:`get_by_id`.

        Args:
            cnx_uuid: UUID to search for
            adapter_name: name of adapter
            adapter_node: name of node running adapter
            **kwargs: passed to :meth:`get_by_key`
        """
        kwargs["value_key"] = "uuid"
        return self.get_by_key(
            value=cnx_uuid,
            adapter_name=adapter_name,
            adapter_node=adapter_node,
            **kwargs,
        )

    def get_by_label(
        self, value: str, adapter_name: str, adapter_node: Optional[str] = None
    ) -> dict:
        """Get a connection for an adapter on a node using a specific connection identifier key.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Get a single connection by connection label

            >>> cnx = client.adapters.cnx.get_by_label(
            ...     value='test label', adapter_name='active_directory'
            ... )

        Args:
            value: value that connection_label must match for a connection
            adapter_name: name of adapter
            adapter_node: name of node running adapter

        Raises:
            :exc:`NotFoundError`: when no connections found with supplied connection label
        """
        key = "connection_label"
        cnxs = self.get_by_adapter(adapter_name=adapter_name, adapter_node=adapter_node)
        for cnx in cnxs:
            config = cnx.get("config") or {}
            label = config.get(key) or ""
            if label == value:
                return cnx

        err = (
            f"No connection found on adapter {adapter_name!r} node {adapter_node!r} "
            f"with a {key} of {value!r}"
        )
        raise NotFoundError(tablize_cnxs(cnxs=cnxs, err=err))

    def get_by_id(
        self, cnx_id: str, adapter_name: str, adapter_node: Optional[str] = None, **kwargs
    ) -> dict:
        """Get a connection for an adapter on a node by ID.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Get a single connection by ID

            >>> cnx = client.adapters.cnx.get_by_id(
            ...     cnx_id='192.168.1.10', adapter_name='active_directory'
            ... )

        Notes:
            ID is constructed from some variance of connection keys, usually "domain"
            (i.e. for active_directory ``TestDomain.test``)

        Args:
            cnx_id: connection ID to get
            adapter_name: name of adapter
            adapter_node: name of node running adapter
            **kwargs: passed to :meth:`get_by_key`
        """
        kwargs["value_key"] = "id"
        return self.get_by_key(
            value=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node, **kwargs
        )

    def update_by_id(
        self, cnx_id: str, adapter_name: str, adapter_node: Optional[str] = None, **kwargs
    ) -> dict:
        """Update a connection for an adapter on a node by ID.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Change the connection label for a connection

            >>> cnx = client.adapters.cnx.update_by_id(
            ...     cnx_id='TestDomain.test',
            ...     adapter_name='active_directory',
            ...     connection_label="new label",
            ... )

        Args:
            cnx_id: connection ID to update
            adapter_name: name of adapter
            adapter_node: name of node running adapter
            **kwargs: passed to :meth:`update_cnx`
        """
        cnx_update = self.get_by_id(
            cnx_id=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node
        )
        return self.update_cnx(cnx_update=cnx_update, **kwargs)

    def delete_by_id(
        self,
        cnx_id: str,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        delete_entities: bool = False,
    ) -> str:
        """Delete a connection for an adapter on a node by connection ID.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Delete a connection by ID

            >>> cnx = client.adapters.cnx.delete_by_id(
            ...     cnx_id='192.168.1.10', adapter_name='active_directory'
            ... )

        Args:
            cnx_id: connection ID to delete
            adapter_name: name of adapter
            adapter_node: name of node running adapter
            delete_entities: delete all asset entities associated with this connection
        """
        cnx_delete = self.get_by_id(
            cnx_id=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node
        )
        return self.delete_cnx(cnx_delete=cnx_delete, delete_entities=delete_entities)

    def test_by_id(self, **kwargs) -> str:
        """Test a connection for an adapter on a node by ID.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Test the reachability of a connection by ID

            >>> cnx = client.adapters.cnx.test_by_id(
            ...     cnx_id='192.168.1.10', adapter_name='active_directory'
            ... )

        Args:
            **kwargs: passed to :meth:`get_by_id`
        """
        cnx = self.get_by_id(**kwargs)
        return self.test_cnx(cnx_test=cnx)

    def test(
        self,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        old_config: Optional[dict] = None,
        **kwargs,
    ) -> str:
        """Test a connection to an adapter on a node.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Test the reachability of a connection without creating the connection

            >>> config = dict(dc_name="192.168.1.10", user="svc_user", password="test")
            >>> cnx = client.adapters.cnx.test(adapter_name="active_directory", **config)

        Notes:
            This can be used to test the configuration of a connection before creating the
            connection. Usually you need just whatever configuration keys are related to
            hostname/domain/ip address to test a connection.

        Args:
            adapter_name: name of adapter
            adapter_node: name of node running adapter
            old_config: old connection configuration
            **kwargs: configuration of connection to test

        Raises:
            :exc:`CnxTestError`: When a connection test fails
            :exc:`ConfigRequired`: When not enough arguments are supplied to test the connection
        """
        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node)
        adapter_name = adapter["name"]
        adapter_name_raw = adapter["name_raw"]
        adapter_node_id = adapter["node_id"]
        adapter_node_name = adapter["node_name"]
        cnx_schemas = adapter["schemas"]["cnx"]

        kwargs_config = kwargs.pop("kwargs_config", {})
        kwargs.update(kwargs_config)

        source = f"reachability test for adapter {adapter_name!r}"

        new_config = self.build_config(
            cnx_schemas=cnx_schemas,
            old_config=old_config,
            new_config=kwargs,
            source=source,
            adapter_name=adapter_name,
            adapter_node=adapter_node_name,
        )

        config_empty(schemas=cnx_schemas, new_config=new_config, source=source)

        result = self._test(
            adapter_name_raw=adapter_name_raw,
            adapter_node_id=adapter_node_id,
            config=new_config,
        )

        rtext = (result.text or "").strip()
        rjson = json_load(obj=rtext, error=False) if rtext else {}

        had_error = not result.ok or bool(rtext)

        if had_error:
            if rjson.get("type") == "AttributeError":
                err = (
                    "Reachability test failed due to settings required for "
                    "testing reachability (supply at least hostname/domain/etc)"
                )
                msg = tablize_schemas(schemas=cnx_schemas, err=err)
                raise ConfigRequired(msg)
            else:
                rkw = ["{}: {}".format(k, v) for k, v in rjson.items()]
                rkw = "\n  " + "\n  ".join(rkw)
                msg = f"Reachability test failed:{rkw}"
                raise CnxTestError(msg)
        return rtext

    def test_cnx(self, cnx_test: dict, **kwargs) -> str:
        """Test a connection for an adapter on a node.

        Args:
            cnx_test: connection fetched previously
            **kwargs: passed to :meth:`test`
        """
        adapter_name = cnx_test["adapter_name"]
        adapter_node = cnx_test["node_name"]
        old_config = cnx_test["config"]
        return self.test(
            adapter_name=adapter_name, adapter_node=adapter_node, old_config=old_config, **kwargs
        )

    def update_cnx(self, cnx_update: dict, **kwargs) -> dict:
        """Update a connection for an adapter on a node.

        Args:
            cnx_test: connection fetched previously
            **kwargs: configuration of connection to update

        Raises:
            :exc:`CnxUpdateError`: When an error occurs while updating the connection
        """
        kwargs_config = kwargs.pop("kwargs_config", {})
        kwargs.update(kwargs_config)

        adapter_name = cnx_update["adapter_name"]
        adapter_name_raw = cnx_update["adapter_name_raw"]
        adapter_node_name = cnx_update["node_name"]
        adapter_node_id = cnx_update["node_id"]
        cnx_schemas = cnx_update["schemas"]

        old_config = cnx_update["config"]
        old_uuid = cnx_update["uuid"]
        old_id = cnx_update["id"]

        source = f"updating settings for connection ID {old_id!r} on adapter {adapter_name!r}"

        new_config = self.build_config(
            cnx_schemas=cnx_schemas,
            old_config=old_config,
            new_config=kwargs,
            source=source,
            adapter_name=adapter_name,
            adapter_node=adapter_node_name,
        )

        config_empty(schemas=cnx_schemas, new_config=new_config, source=source)

        config_unchanged(
            schemas=cnx_schemas,
            old_config=old_config,
            new_config=new_config,
            source=source,
        )

        result = self._update(
            adapter_name_raw=adapter_name_raw,
            adapter_node_id=adapter_node_id,
            new_config=new_config,
            cnx_uuid=old_uuid,
        )

        # XXX need to validate error handling!!!!!!!
        if not isinstance(result, dict) or not result:  # pragma: no cover
            result = {"error": result}

        self.check_if_gone(
            result=result,
            cnx_id=old_id,
            adapter_name=adapter_name,
            adapter_node=adapter_node_name,
        )

        result_status = result.get("status", "")
        result_error = result.get("error", "")
        result_id = result.get("id", "")
        status_is_error = result_status == "error"

        if result_id:
            cnx_new = self.get_by_uuid(
                cnx_uuid=result_id,
                adapter_name=adapter_name,
                adapter_node=adapter_node_name,
                retry=CNX_RETRY,
            )
        else:  # pragma: no cover
            cnx_new = self.get_by_id(
                cnx_id=old_id, adapter_name=adapter_name, adapter_node=adapter_node_name
            )

        if any([status_is_error, result_error]):
            rkw = ["{}: {}".format(k, v) for k, v in result.items()]
            rkw = "\n  " + "\n  ".join(rkw)

            err = f"Connection was updated but had a failure connecting:{rkw}"
            exc = CnxUpdateError(err)

            exc.result = result
            exc.cnx_old = cnx_update
            exc.cnx_new = cnx_new

            raise exc

        return cnx_new

    def delete_cnx(self, cnx_delete: dict, delete_entities: bool = False) -> str:
        """Delete a connection for an adapter on a node.

        Args:
            cnx_delete: connection fetched previously
            delete_entities: delete all asset entities associated with this connection
        """
        adapter_name_raw = cnx_delete["adapter_name_raw"]
        adapter_node_id = cnx_delete["node_id"]
        cnx_uuid = cnx_delete["uuid"]

        return self._delete(
            adapter_name_raw=adapter_name_raw,
            adapter_node_id=adapter_node_id,
            cnx_uuid=cnx_uuid,
            delete_entities=delete_entities,
        )

    def check_if_gone(self, result: dict, cnx_id: str, adapter_name: str, adapter_node: str):
        """Check if the result of updating a connection shows that the connection is gone.

        Args:
            result: JSON response from updating a connection
            cnx_id: connection ID that was being updated
            adapter_name: name of adapter
            adapter_node: name of node running adapter

        Raises:
            :exc:`CnxGoneError`: when a connection is updated by someone
                causing the connections UUID or ID to change
        """
        message = result.get("message", "")
        if message == CNX_GONE:
            cnxs = self.get_by_adapter(adapter_name=adapter_name, adapter_node=adapter_node)
            err = f"Connection with ID {cnx_id!r} no longer exists!"
            raise CnxGoneError(tablize_cnxs(cnxs=cnxs, err=err))

    def build_config(
        self,
        cnx_schemas: List[dict],
        new_config: dict,
        source: str,
        adapter_name: str,
        adapter_node: str,
        old_config: Optional[dict] = None,
    ) -> dict:
        """Build and parse a configuration for a connection.

        Args:
            cnx_schemas: configuration schemas for connection
            new_config: new configuration for connection
            source: description of what called this method
            adapter_name: name of adapter
            adapter_node: name of node running adapter
            old_config: configuration that is being updated
        """
        old_config = old_config or {}
        callbacks = {
            "cb_file": self.cb_file_upload,
            "adapter_name": adapter_name,
            "adapter_node": adapter_node,
        }

        config_unknown(
            schemas=cnx_schemas,
            new_config=new_config,
            source=source,
            callbacks=callbacks,
        )

        new_config = config_build(
            schemas=cnx_schemas,
            old_config=old_config,
            new_config=new_config,
            source=source,
            callbacks=callbacks,
        )

        return new_config

    def get_sane_defaults(self, adapter_name: str) -> dict:
        """Get the API client defined sane defaults for a specific adapter.

        Args:
            adapter_name: name of adapter
        """
        return CNX_SANE_DEFAULTS.get(adapter_name, CNX_SANE_DEFAULTS["all"])

    def get_by_key(
        self,
        value: str,
        value_key: str,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        retry: int = 0,
        sleep: int = 1,
    ) -> dict:
        """Get a connection for an adapter on a node using a specific connection identifier key.

        Args:
            value: value that value_key must match for a connection
            value_key: name of connection key to search for value of
            adapter_name: name of adapter
            adapter_node: name of node running adapter
            retry: number of times to retry to find the connection using value_key[value]
            sleep: seconds to sleep in between each retry

        Raises:
            :exc:`NotFoundError`: when no connection found where value == cnx[value_key]
        """
        tries = 1
        cnxs = self.get_by_adapter(adapter_name=adapter_name, adapter_node=adapter_node)
        while True:
            for cnx in cnxs:
                if cnx[value_key] == value:
                    return cnx

            tries += 1

            if tries > retry:
                break

            time.sleep(sleep)

            cnxs = self.get_by_adapter(adapter_name=adapter_name, adapter_node=adapter_node)

        value_key = value_key.upper()
        err = (
            f"No connection found on adapter {adapter_name!r} node {adapter_node!r} "
            f"with {value_key} of {value!r}"
        )
        raise NotFoundError(tablize_cnxs(cnxs=cnxs, err=err))

    def cb_file_upload(
        self,
        value: Union[str, pathlib.Path, dict],
        schema: dict,
        callbacks: dict,
        source: str,
    ) -> dict:
        """Config parsing callback to upload a file for a connection.

        Args:
            value: file to upload
            schema: connection configuration schema of type "file"
            callbacks: callbacks supplied
            source: description of what called this method

        Raises:
            :exc:`ConfigInvalidValue`: When value is a path that does not exist, or
                a dictionary that does not have 'uuid' and 'filename' keys',
                or if value is not a file
        """
        adapter_name = callbacks["adapter_name"]
        adapter_node = callbacks["adapter_node"]
        field_name = schema["name"]

        value = json_load(obj=value, error=False)

        if isinstance(value, str):
            value = pathlib.Path(value).expanduser().resolve()
            if not value.is_file():
                sinfo = config_info(schema=schema, value=str(value), source=source)
                raise ConfigInvalidValue(f"{sinfo}\nFile does not exist!")
            return self.parent.file_upload(
                name=adapter_name,
                field_name=field_name,
                file_name=value.name,
                file_content=value.read_text(),
                node=adapter_node,
            )

        if isinstance(value, dict):
            if value.get("uuid") and value.get("filename"):
                return {"uuid": value["uuid"], "filename": value["filename"]}

            sinfo = config_info(schema=schema, value=str(value), source=source)
            raise ConfigInvalidValue(
                f"{sinfo}\nDictionary must have uuid and filename keys: {value}!"
            )

        if isinstance(value, pathlib.Path):
            value = value.expanduser().resolve()
            if not value.is_file():
                sinfo = config_info(schema=schema, value=str(value), source=source)
                raise ConfigInvalidValue(f"{sinfo}\nFile does not exist!")

            return self.parent.file_upload(
                name=adapter_name,
                field_name=field_name,
                file_name=value.name,
                file_content=value.read_text(),
                node=adapter_node,
            )

        sinfo = config_info(schema=schema, value=str(value), source=source)
        raise ConfigInvalidValue(f"{sinfo}\nFile is not an existing file!")

    # XXX failing with secondary node!!! wrong plugin name?
    def _add(self, adapter_name_raw: str, adapter_node_id: str, new_config: dict) -> str:
        """Private API method to add a connection to an adapter.

        Args:
            adapter_name_raw: raw name of the adapter i.e. ``aws_adapter``
            adapter_node_id: id of node running adapter
            new_config: configuration of new connection
        """
        data = {}
        data.update(new_config)
        data["instanceName"] = adapter_node_id

        path = self.parent.router.cnxs.format(adapter_name_raw=adapter_name_raw)

        return self.parent.request(
            method="put",
            path=path,
            json=data,
            error_json_bad_status=False,
            error_status=False,
        )

    def _test(self, adapter_name_raw: str, adapter_node_id: str, config: dict) -> str:
        """Private API method to add a connection to an adapter.

        Args:
            adapter_name_raw: raw name of the adapter i.e. ``aws_adapter``
            adapter_node_id: id of node running adapter
            config: configuration to test
        """
        data = {}
        data.update(config)
        data["instanceName"] = adapter_node_id
        data["oldInstanceName"] = adapter_node_id

        path = self.parent.router.cnxs_test.format(adapter_name_raw=adapter_name_raw)
        return self.parent.request(method="post", path=path, json=data, raw=True)

    def _delete(
        self,
        adapter_name_raw: str,
        adapter_node_id: str,
        cnx_uuid: str,
        delete_entities: bool = False,
    ) -> str:
        """Private API method to delete a connection from an adapter.

        Args:
            adapter_name_raw: raw name of the adapter i.e. ``aws_adapter``
            adapter_node_id: id of node running adapter
            cnx_uuid: uuid of connection to delete
            delete_entities: delete all asset entities associated with this connection
        """
        data = {}
        data["instanceName"] = adapter_node_id

        params = {"deleteEntities": delete_entities}

        path = self.parent.router.cnxs_uuid.format(
            adapter_name_raw=adapter_name_raw, cnx_uuid=cnx_uuid
        )

        return self.parent.request(
            method="delete",
            path=path,
            json=data,
            params=params,
            error_json_bad_status=False,
            error_status=False,
        )

    def _update(
        self,
        adapter_name_raw: str,
        adapter_node_id: str,
        new_config: dict,
        cnx_uuid: str,
    ) -> str:
        """Private API method to update a connection on an adapter.

        Args:
            adapter_name_raw: raw name of the adapter i.e. ``aws_adapter``
            adapter_node_id: id of node running adapter
            cnx_uuid: uuid of connection to delete
            new_config: configuration of connection
        """
        data = {}
        data.update(new_config)
        data["instanceName"] = adapter_node_id
        data["oldInstanceName"] = adapter_node_id

        path = self.parent.router.cnxs_uuid.format(
            adapter_name_raw=adapter_name_raw, cnx_uuid=cnx_uuid
        )
        return self.parent.request(
            method="post",
            path=path,
            json=data,
            error_json_bad_status=False,
            error_status=False,
        )
