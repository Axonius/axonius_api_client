# -*- coding: utf-8 -*-
"""API for working with adapter connections."""
from typing import Callable, List, Optional, Union

from ...constants.adapters import CNX_SANE_DEFAULTS
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
from ...tools import json_dump, json_load, listify, pathlib
from .. import json_api
from ..api_endpoints import ApiEndpoints
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

    def add(
        self,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        save_and_fetch: bool = True,
        active: bool = True,
        connection_label: Optional[str] = None,
        kwargs_config: Optional[dict] = None,
        **kwargs,
    ) -> dict:
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
        new_config = {}
        new_config.update(kwargs_config or {})
        new_config.update(kwargs)

        adapter_meta = self.parent.get_by_name(
            name=adapter_name, node=adapter_node, get_clients=False
        )

        adapter_name = adapter_meta["name"]
        adapter_name_raw = adapter_meta["name_raw"]
        node_name = adapter_meta["node_meta"]["name"]
        node_id = adapter_meta["node_meta"]["id"]
        is_instances_mode = not adapter_meta["node_meta"]["is_master"]

        cnxs = self._get(adapter_name=adapter_name_raw)
        cnx_schemas = cnxs.schema_cnx

        source = f"adding connection for adapter {adapter_name!r}"

        new_config = self.build_config(
            cnx_schemas=cnx_schemas,
            new_config=new_config,
            source=source,
            adapter_name=adapter_name,
            adapter_node=node_name,
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
            connection=new_config,
            adapter_name=adapter_name_raw,
            instance_name=node_name,
            instance_id=node_id,
            is_instances_mode=is_instances_mode,
            save_and_fetch=save_and_fetch,
            active=active,
            connection_label=connection_label,
        )

        cnx_new = self.get_by_uuid(
            cnx_uuid=result.id,
            adapter_name=adapter_name,
            adapter_node=node_name,
        )

        if not result.working:
            err = f"Connection was added but had a failure connecting:\n{result}"
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
        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        node = adapter["node_meta"]
        cnxs_obj = self._get(adapter_name=adapter["name_raw"])
        cnxs = [x for x in cnxs_obj.cnxs if x.node_id == node["node_id"]]
        return [x.to_dict_old() for x in cnxs]

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
        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        node = adapter["node_meta"]
        node_id = node["node_id"]
        node_name = node["node_name"]
        cnxs_obj = self._get(adapter_name=adapter["name_raw"])

        for cnx in cnxs_obj.cnxs:
            if all([cnx.node_id == node_id, cnx.uuid == cnx_uuid]):
                return cnx.to_dict_old()

        err = (
            f"No connection found on adapter {adapter_name!r} node {node_name!r} "
            f"with UUID of {cnx_uuid!r}"
        )
        cnxs = [x.to_dict_old() for x in cnxs_obj.cnxs]
        raise NotFoundError(tablize_cnxs(cnxs=cnxs, err=err))

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
        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        node = adapter["node_meta"]
        node_id = node["node_id"]
        node_name = node["node_name"]
        cnxs_obj = self._get(adapter_name=adapter["name_raw"])

        for cnx in cnxs_obj.cnxs:
            if all([cnx.node_id == node_id, cnx.connection_label == value]):
                return cnx.to_dict_old()

        err = (
            f"No connection found on adapter {adapter_name!r} node {node_name!r} "
            f"with a connection label of {value!r}"
        )
        cnxs = [x.to_dict_old() for x in cnxs_obj.cnxs]
        raise NotFoundError(tablize_cnxs(cnxs=cnxs, err=err))

    # TBD: should support CID or UUID for get_by
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
        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        node = adapter["node_meta"]
        node_id = node["node_id"]
        node_name = node["node_name"]

        cnxs_obj = self._get(adapter_name=adapter["name_raw"])

        for cnx in cnxs_obj.cnxs:
            if all([cnx.node_id == node_id, cnx.client_id == cnx_id]):
                return cnx.to_dict_old()

        err = (
            f"No connection found on adapter {adapter_name!r} node {node_name!r} "
            f"with ID of {cnx_id!r}"
        )
        cnxs = [x.to_dict_old() for x in cnxs_obj.cnxs]
        raise NotFoundError(tablize_cnxs(cnxs=cnxs, err=err))

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
        cnx = self.get_by_id(cnx_id=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node)
        return self.update_cnx(cnx_update=cnx, **kwargs)

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
        cnx = self.get_by_id(cnx_id=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node)
        return self.delete_cnx(cnx_delete=cnx, delete_entities=delete_entities)

    def test_by_id(self, **kwargs) -> bool:
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
        kwargs_config: Optional[dict] = None,
        **kwargs,
    ) -> bool:
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
        new_config = {}
        new_config.update(kwargs_config or {})
        new_config.update(kwargs)

        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        adapter_name = adapter["name"]
        adapter_name_raw = adapter["name_raw"]
        node_id = adapter["node_id"]
        node_name = adapter["node_name"]

        cnxs_obj = self._get(adapter_name=adapter_name_raw)
        schemas = cnxs_obj.schema_cnx

        deets = [
            f"Adapter: {adapter_name!r}",
            f"Node: {node_name}",
        ]
        deets = ", ".join(deets)
        source = f"connectivity test for {deets}"

        new_config = self.build_config(
            cnx_schemas=schemas,
            old_config={},
            new_config=new_config,
            source=source,
            adapter_name=adapter_name,
            adapter_node=node_name,
        )

        config_empty(schemas=schemas, new_config=new_config, source=source)

        test_hook = self._get_test_hook(schemas=schemas, adapter=adapter_name, node=node_name)
        self._test(
            adapter_name=adapter_name_raw,
            instance=node_id,
            connection=new_config,
            response_status_hook=test_hook,
        )
        return True

    def test_cnx(self, cnx_test: dict, **kwargs) -> bool:
        """Test a connection for an adapter on a node.

        Args:
            cnx_test: connection fetched previously
            **kwargs: passed to :meth:`test`
        """
        adapter_name = cnx_test["adapter_name"]
        adapter_name_raw = cnx_test["adapter_name_raw"]
        node_name = cnx_test["node_name"]
        node_id = cnx_test["node_id"]
        config = cnx_test["config"]
        uuid = cnx_test["uuid"]
        cid = cnx_test["id"]
        schemas = cnx_test["schemas"]

        test_hook = self._get_test_hook(
            schemas=schemas, adapter=adapter_name, node=node_name, uuid=uuid, cid=cid
        )
        self._test(
            adapter_name=adapter_name_raw,
            instance=node_id,
            connection=config,
            response_status_hook=test_hook,
        )
        return True

    def set_cnx_active(self, cnx: dict, value: bool, save_and_fetch: bool = False):
        """Pass."""
        adapter_name = cnx["adapter_name"]
        adapter_name_raw = cnx["adapter_name_raw"]
        node_name = cnx["node_name"]
        node_id = cnx["node_id"]
        connection_label = cnx["connection_label"]
        config = cnx["config"]
        uuid = cnx["uuid"]
        cid = cnx["id"]

        node_meta = self.parent.instance.get_by_name(name=node_name)
        is_instances_mode = not node_meta["is_master"]

        gone_hook = self._get_gone_hook(cid=cid, uuid=uuid, adapter=adapter_name, node=node_name)

        result = self._update(
            connection=config,
            adapter_name=adapter_name_raw,
            instance_name=node_name,
            instance_id=node_id,
            instance_prev=node_id,
            instance_prev_name=node_name,
            is_instances_mode=is_instances_mode,
            save_and_fetch=save_and_fetch,
            active=value,
            connection_label=connection_label,
            response_status_hook=gone_hook,
        )

        cnx_new = self.get_by_uuid(
            cnx_uuid=result.id,
            adapter_name=adapter_name,
            adapter_node=node_name,
        )

        return cnx_new

    def set_cnx_label(self, cnx: dict, value: str, save_and_fetch: bool = False):
        """Pass."""
        adapter_name = cnx["adapter_name"]
        adapter_name_raw = cnx["adapter_name_raw"]
        node_name = cnx["node_name"]
        node_id = cnx["node_id"]
        config = cnx["config"]
        active = cnx["active"]
        uuid = cnx["uuid"]
        cid = cnx["id"]

        node_meta = self.parent.instances.get_by_name(name=node_name)
        is_instances_mode = not node_meta["is_master"]

        gone_hook = self._get_gone_hook(cid=cid, uuid=uuid, adapter=adapter_name, node=node_name)

        result = self._update(
            uuid=uuid,
            connection=config,
            adapter_name=adapter_name_raw,
            instance_name=node_name,
            instance_id=node_id,
            instance_prev=node_id,
            instance_prev_name=node_name,
            is_instances_mode=is_instances_mode,
            save_and_fetch=save_and_fetch,
            active=active,
            connection_label=value,
            response_status_hook=gone_hook,
        )

        cnx_new = self.get_by_uuid(
            cnx_uuid=result.id,
            adapter_name=adapter_name,
            adapter_node=node_name,
        )

        return cnx_new

    def update_cnx(
        self,
        cnx_update: dict,
        save_and_fetch: bool = True,
        kwargs_config: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        """Update a connection for an adapter on a node.

        Args:
            cnx_update: connection fetched previously
            **kwargs: configuration of connection to update

        Raises:
            :exc:`CnxUpdateError`: When an error occurs while updating the connection
        """
        new_config = {}
        new_config.update(kwargs_config or {})
        new_config.update(kwargs)

        adapter_name = cnx_update["adapter_name"]
        adapter_name_raw = cnx_update["adapter_name_raw"]
        node_name = cnx_update["node_name"]
        node_id = cnx_update["node_id"]
        cnx_schemas = cnx_update["schemas"]
        active = cnx_update["active"]
        label = cnx_update["connection_label"]
        uuid = cnx_update["uuid"]

        node_meta = self.parent.instances.get_by_name(name=node_name)
        is_instances_mode = not node_meta["is_master"]

        old_config = cnx_update["config"]
        uuid = cnx_update["uuid"]
        cid = cnx_update["id"]

        deets = [
            f"ID: {cid!r}",
            f"UUID: {uuid}",
            f"Adapter: {adapter_name!r}",
            f"Node: {node_name}",
        ]
        deets = ", ".join(deets)
        source = f"updating settings for connection {deets}"

        new_config = self.build_config(
            cnx_schemas=cnx_schemas,
            old_config=old_config,
            new_config=new_config,
            source=source,
            adapter_name=adapter_name,
            adapter_node=node_name,
        )

        config_empty(schemas=cnx_schemas, new_config=new_config, source=source)

        config_unchanged(
            schemas=cnx_schemas,
            old_config=old_config,
            new_config=new_config,
            source=source,
        )

        gone_hook = self._get_gone_hook(cid=cid, uuid=uuid, adapter=adapter_name, node=node_name)

        result = self._update(
            uuid=uuid,
            connection=new_config,
            adapter_name=adapter_name_raw,
            instance_name=node_name,
            instance_id=node_id,
            instance_prev=node_id,
            instance_prev_name=node_name,
            is_instances_mode=is_instances_mode,
            save_and_fetch=save_and_fetch,
            active=active,
            connection_label=label,
            response_status_hook=gone_hook,
        )

        cnx_new = self.get_by_uuid(
            cnx_uuid=result.id,
            adapter_name=adapter_name,
            adapter_node=node_name,
        )

        if not result.working:
            err = f"Connection configuration was updated but had a failure connecting:\n{result}"
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
        adapter_name = cnx_delete["adapter_name"]
        adapter_name_raw = cnx_delete["adapter_name_raw"]
        node_name = cnx_delete["node_name"]
        node_id = cnx_delete["node_id"]

        uuid = cnx_delete["uuid"]
        cid = cnx_delete["id"]

        node = self.parent.instances.get_by_name(name=cnx_delete["node_name"])
        node_id = node["id"]
        node_name = node["name"]
        is_instances_mode = not node["is_master"]

        gone_hook = self._get_gone_hook(cid=cid, uuid=uuid, adapter=adapter_name, node=node_name)

        return self._delete(
            adapter_name=adapter_name_raw,
            uuid=uuid,
            delete_entities=delete_entities,
            instance_id=node_id,
            instance_name=node_name,
            is_instances_mode=is_instances_mode,
            response_status_hook=gone_hook,
        )

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

    def _get_gone_hook(self, cid: str, uuid: str, adapter: str, node: str):
        """Check if the result of updating a connection shows that the connection is gone."""

        def hook(http, response, **kwargs):
            """Pass."""
            apiobj = self
            cnx_cid = cid
            cnx_uuid = uuid
            cnx_adapter = adapter
            cnx_node = node

            deets = [
                f"Adapter: {cnx_adapter!r}",
                f"Node: {cnx_node!r}",
                f"ID: {cnx_cid!r}",
                f"UUID: {cnx_uuid!r}",
            ]
            deets = ", ".join(deets)

            data = json_load(obj=response.text, error=False)
            if not isinstance(data, dict):
                return

            errors = listify(data.get("errors"))

            for error in errors:
                if not isinstance(error, dict):
                    continue

                detail = error.get("detail")

                if "already gone" in str(detail).lower():
                    cnxs = apiobj.get_by_adapter(adapter_name=adapter, adapter_node=node)
                    msg = f"Connection is gone - updated or deleted by someone else!\n{deets}"
                    err = tablize_cnxs(cnxs=cnxs, err=msg)
                    raise CnxGoneError(err)

        return hook

    def _get_test_hook(
        self,
        schemas: List[dict],
        adapter: str,
        node: str,
        cid: Optional[str] = None,
        uuid: Optional[str] = None,
    ):
        """Check if the result of testing a connection shows has various failures."""

        def hook(http, response, **kwargs):
            """Pass."""
            cnx_schemas = schemas
            cnx_cid = cid
            cnx_uuid = uuid
            cnx_adapter = adapter
            cnx_node = node
            deets = [
                f"Adapter: {cnx_adapter!r}",
                f"Node: {cnx_node!r}",
                f"ID: {cnx_cid!r}" if cnx_cid else "",
                f"UUID: {cnx_uuid!r}" if cnx_uuid else "",
            ]

            deets = ", ".join([x for x in deets if x])

            data = json_load(obj=response.text, error=False)

            if not isinstance(data, dict):
                return

            data_request = json_load(obj=response.request.body, error=False)

            try:
                config = data_request["data"]["attributes"]["connection"]
            except Exception:
                config = {}

            config_json = json_dump(obj=config, error=False)
            config_txt = f"on {deets} with configuration:\n{config_json}"
            response_json = json_dump(obj=data, error=False)
            response_txt = f"Connectivty test failure, response:\n{response_json}"

            errors = listify(data.get("errors"))

            exc = None
            pre = ""

            # PBUG: this nasty footwork should be server side
            for error in errors:
                if not isinstance(error, dict):
                    continue

                detail = error.get("detail")

                if "invalid client" in str(detail).lower():
                    pre = "Invalid/missing domain or other connection parameter"
                    exc = ConfigRequired
                    # only happens if connection is empty

                if "not reachable" in str(detail).lower():
                    pre = "Connectivity test failed"
                    exc = CnxTestError

            if not exc and data.get("meta") == 400:
                pre = "Invalid/missing domain or other connection parameter"
                exc = ConfigRequired
                # PBUG: with domain=None, {'data': null, 'meta': 400}

            if exc:
                msg = f"{pre} {config_txt}"
                err = tablize_schemas(schemas=cnx_schemas, err=msg)
                raise exc(f"{response_txt}\n{err}")

        return hook

    def _add(
        self,
        connection: dict,
        instance_id: str,
        instance_name: str,
        adapter_name: str,
        connection_discovery: Optional[dict] = None,
        is_instances_mode: bool = False,
        save_and_fetch: bool = True,
        active: bool = True,
        connection_label: Optional[str] = None,
    ) -> json_api.adapters.CnxModifyResponse:
        """Pass."""
        api_endpoint = ApiEndpoints.adapters.cnx_create
        request_obj = api_endpoint.load_request(
            connection=connection,
            connection_discovery=connection_discovery,
            instance=instance_id,
            instance_name=instance_name,
            is_instances_mode=is_instances_mode,
            active=active,
            save_and_fetch=save_and_fetch,
            connection_label=connection_label,
        )
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, adapter_name=adapter_name
        )

    def _test(
        self,
        adapter_name: str,
        instance: str,
        connection: dict,
        response_status_hook: Optional[Callable] = None,
    ) -> dict:
        """Private API method to add a connection to an adapter.

        Args:
            adapter_name_raw: raw name of the adapter i.e. ``aws_adapter``
            adapter_node_id: id of node running adapter
            config: configuration to test
        """
        api_endpoint = ApiEndpoints.adapters.cnx_test
        request_obj = api_endpoint.load_request(
            connection=connection,
            instance=instance,
        )
        return api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            adapter_name=adapter_name,
            response_status_hook=response_status_hook,
        )

    def _get(self, adapter_name: str) -> json_api.adapters.Cnxs:
        """Pass."""
        api_endpoint = ApiEndpoints.adapters.cnx_get
        return api_endpoint.perform_request(http=self.auth.http, adapter_name=adapter_name)

    def _delete(
        self,
        uuid: str,
        adapter_name: str,
        instance_id: str,
        instance_name: str,
        delete_entities: bool = False,
        is_instances_mode: bool = False,
        response_status_hook: Optional[Callable] = None,
    ) -> json_api.adapters.CnxDelete:
        """Private API method to delete a connection from an adapter.

        Args:
            adapter_name_raw: raw name of the adapter i.e. ``aws_adapter``
            adapter_node_id: id of node running adapter
            uuid: uuid of connection to delete
            delete_entities: delete all asset entities associated with this connection
        """
        api_endpoint = ApiEndpoints.adapters.cnx_delete
        request_obj = api_endpoint.load_request(
            instance=instance_id,
            instance_name=instance_name,
            delete_entities=delete_entities,
            is_instances_mode=is_instances_mode,
        )
        return api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            adapter_name=adapter_name,
            uuid=uuid,
            response_status_hook=response_status_hook,
        )

    def _update(
        self,
        uuid: str,
        connection: dict,
        instance_id: str,
        instance_name: str,
        adapter_name: str,
        instance_prev: Optional[str] = None,
        instance_prev_name: Optional[str] = None,
        connection_discovery: Optional[dict] = None,
        is_instances_mode: bool = False,
        save_and_fetch: bool = True,
        active: bool = True,
        connection_label: Optional[str] = None,
        response_status_hook: Optional[Callable] = None,
    ) -> json_api.adapters.CnxModifyResponse:
        """Pass."""
        api_endpoint = ApiEndpoints.adapters.cnx_update
        request_obj = api_endpoint.load_request(
            connection=connection,
            connection_discovery=connection_discovery,
            instance=instance_id,
            instance_name=instance_name,
            instance_prev=instance_prev,
            instance_prev_name=instance_prev_name,
            is_instances_mode=is_instances_mode,
            active=active,
            save_and_fetch=save_and_fetch,
            connection_label=connection_label,
        )
        return api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            adapter_name=adapter_name,
            uuid=uuid,
            response_status_hook=response_status_hook,
        )
