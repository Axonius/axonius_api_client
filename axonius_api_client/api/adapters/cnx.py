# -*- coding: utf-8 -*-
"""API for working with adapter connections."""
import dataclasses
import re
from typing import Callable, List, Optional, Type, Union

import requests

from ...constants.adapters import CNX_SANE_DEFAULTS
from ...exceptions import (
    CnxAddError,
    CnxError,
    CnxGoneError,
    CnxTestError,
    CnxUpdateError,
    ConfigInvalidValue,
    ConfigRequired,
    NotFoundError,
)
from ...http import Http
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
from ...tools import (
    combo_dicts,
    is_existing_file,
    json_dump,
    json_load,
    listify,
    pathify,
    pathlib,
    strip_right,
)
from ..api_endpoints import ApiEndpoints
from ..json_api.adapters import CnxCreate, CnxDelete, CnxLabels, Cnxs, CnxUpdate
from ..json_api.instances import Tunnel
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

    def get_by_adapter(
        self,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        tunnel: Optional[Union[Tunnel, str]] = None,
    ) -> List[dict]:
        """Get all connections of an adapter on a node.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Get all connections for an adapter on the Core instance

            >>> cnxs = client.adapters.cnx.get_by_adapter(adapter_name="active_directory")

        Args:
            adapter_name (str): name of adapter
            adapter_node (Optional[str], optional): name of node running adapter
            tunnel (Optional[str], optional): name or ID of tunnel

        Returns:
            List[dict]: connection metadata for adapter
        """

        def is_match(cnx):
            if cnx.node_id != adapter["node_meta"]["node_id"]:
                return False
            if (tunnel_obj and cnx.tunnel_id) and tunnel_obj.id != cnx.tunnel_id:
                return False
            return True

        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        tunnel_obj = self.parent.instances.get_tunnel(value=tunnel)
        cnxs_obj = self._get(adapter_name=adapter["name_raw"])
        ret = [x for x in cnxs_obj.cnxs if is_match(x)]
        return [x.to_dict_old() for x in ret]

    def get_by_uuid(
        self,
        cnx_uuid: str,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        tunnel: Optional[Union[Tunnel, str]] = None,
        **kwargs,
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
            tunnel (Optional[str], optional): name or ID of tunnel
            **kwargs: passed to :meth:`get_by_key`

        Raises:
            NotFoundError: when no connections found with supplied uuid

        Returns:
            dict: connection metadata for uuid on adapter
        """

        def is_match(cnx):
            if cnx.node_id != adapter["node_meta"]["node_id"]:
                return False
            if (tunnel_obj and cnx.tunnel_id) and tunnel_obj.id != cnx.tunnel_id:
                return False
            if cnx_uuid in [cnx.client_id, cnx.uuid]:
                return True
            return False

        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        tunnel_obj = self.parent.instances.get_tunnel(value=tunnel)
        node_name = adapter["node_meta"]["node_name"]
        cnxs_obj = self._get(adapter_name=adapter["name_raw"])

        for cnx in cnxs_obj.cnxs:
            if is_match(cnx=cnx):
                return cnx.to_dict_old()

        err = (
            f"No connection found on adapter {adapter_name!r} node {node_name!r} "
            f"with client ID or UUID of {cnx_uuid!r}"
        )
        if tunnel_obj:
            err += f"on tunnel {tunnel_obj}"

        cnxs = [x.to_dict_old() for x in cnxs_obj.cnxs]
        raise NotFoundError(tablize_cnxs(cnxs=cnxs, err=err))

    def get_by_label(
        self,
        value: str,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        tunnel: Optional[Union[Tunnel, str]] = None,
    ) -> dict:
        """Get a connection for an adapter on a node using a specific connection identifier key.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Get a single connection by connection label

            >>> cnx = client.adapters.cnx.get_by_label(
            ...     value='test label', adapter_name='active_directory'
            ... )

        Args:
            value (str): value that connection_label must match for a connection
            adapter_name (str): name of adapter
            adapter_node (Optional[str], optional): name of node running adapter
            tunnel (Optional[str], optional): name or ID of tunnel

        Raises:
            NotFoundError: when no connections found with supplied connection label

        Returns:
            dict: connection metadata for label on adapter
        """

        def is_match(cnx):
            if cnx.node_id != node_id:
                return False
            if (tunnel_obj and cnx.tunnel_id) and tunnel_obj.id != cnx.tunnel_id:
                return False
            if value == cnx.connection_label:
                return True
            return False

        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        node_id = adapter["node_meta"]["node_id"]
        node_name = adapter["node_meta"]["node_name"]
        cnxs_obj = self._get(adapter_name=adapter["name_raw"])
        tunnel_obj = self.parent.instances.get_tunnel(value=tunnel)

        for cnx in cnxs_obj.cnxs:
            if is_match(cnx=cnx):
                return cnx.to_dict_old()

        err = (
            f"No connection found on adapter {adapter_name!r} node {node_name!r} "
            f"with a connection label of {value!r}"
        )
        if tunnel_obj:
            err += f"on tunnel {tunnel_obj}"

        cnxs = [x.to_dict_old() for x in cnxs_obj.cnxs]
        raise NotFoundError(tablize_cnxs(cnxs=cnxs, err=err))

    def get_by_id(
        self,
        cnx_id: str,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        tunnel: Optional[Union[Tunnel, str]] = None,
        **kwargs,
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
            cnx_id (str): connection ID to get
            adapter_name (str): name of adapter
            adapter_node (Optional[str], optional): name of node running
            tunnel (Optional[str], optional): name or ID of tunnel
            **kwargs: passed to :meth:`get_by_key`

        Raises:
            NotFoundError: when no connections found with supplied id

        Returns:
            dict: connection metadata for id on adapter
        """

        def is_match(cnx):
            if cnx.node_id != node_id:
                return False
            if (tunnel_obj and cnx.tunnel_id) and tunnel_obj.id != cnx.tunnel_id:
                return False
            if cnx_id in [cnx.client_id, cnx.uuid]:
                return True
            return False

        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        node_id = adapter["node_meta"]["node_id"]
        node_name = adapter["node_meta"]["node_name"]
        cnxs_obj = self._get(adapter_name=adapter["name_raw"])
        tunnel_obj = self.parent.instances.get_tunnel(value=tunnel)

        for cnx in cnxs_obj.cnxs:
            if is_match(cnx=cnx):
                return cnx.to_dict_old()

        err = (
            f"No connection found on adapter {adapter_name!r} node {node_name!r} "
            f"with client ID or UUID of {cnx_id!r}"
        )
        if tunnel_obj:
            err += f"on tunnel {tunnel_obj}"

        cnxs = [x.to_dict_old() for x in cnxs_obj.cnxs]
        raise NotFoundError(tablize_cnxs(cnxs=cnxs, err=err))

    def update_by_id(
        self,
        cnx_id: str,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        tunnel: Optional[Union[Tunnel, str]] = None,
        **kwargs,
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
            tunnel (Optional[str], optional): name or ID of tunnel
            **kwargs: passed to :meth:`update_cnx`

        Returns:
            dict: updated connection metadata
        """
        cnx = self.get_by_id(
            cnx_id=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node, tunnel=tunnel
        )
        return self.update_cnx(cnx_update=cnx, **kwargs)

    def delete_by_id(
        self,
        cnx_id: str,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        tunnel: Optional[Union[Tunnel, str]] = None,
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
            tunnel (Optional[str], optional): name or ID of tunnel
            delete_entities: delete all assets fetched by this connection
        """
        cnx = self.get_by_id(
            cnx_id=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node, tunnel=tunnel
        )
        return self.delete_cnx(cnx_delete=cnx, delete_entities=delete_entities)

    def test_by_id(self, **kwargs) -> dict:
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

    def add(
        self,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        save_and_fetch: bool = True,
        active: bool = True,
        tunnel: Optional[Union[Tunnel, str]] = None,
        connection_label: Optional[str] = None,
        kwargs_config: Optional[dict] = None,
        new_config: Optional[dict] = None,
        parse_config: bool = True,
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
            save_and_fetch: perform a fetch when saving, or just save without fetching
            active: set the connection as active after creating
            connection_label: label to assign to connection
            tunnel: tunnel ID or name to use for new connection
            kwargs_config: connection args that conflict with this methods signature
            new_config: connection args that conflict with this methods signature
            parse_config: perform api client side parsing of connection args
            **kwargs: configuration of new connection

        Raises:
            :exc:`CnxAddError`: when an error happens while adding the connection
        """
        new_config = combo_dicts(kwargs_config, new_config, kwargs)
        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        tunnel_id = self.parent.instances.get_tunnel(value=tunnel, return_id=True)
        schemas = self._get(adapter_name=adapter["name_raw"]).schema_cnx
        config_label = new_config.pop("connection_label", None)
        connection_label = connection_label or config_label
        cnx_to_add = cnx_from_adapter(adapter)
        cnx_to_add = combo_dicts(cnx_to_add, config=new_config, schemas=schemas)
        if parse_config:
            cnx_str = ", ".join(get_cnx_strs(cnx=cnx_to_add))
            source = f"adding connection {cnx_str}"

            new_config = self.build_config(
                cnx_schemas=schemas,
                new_config=new_config,
                source=source,
                adapter_name=adapter["name"],
                adapter_node=adapter["node_meta"]["name"],
            )

            config_default(
                schemas=schemas,
                new_config=new_config,
                source=source,
                sane_defaults=self.get_sane_defaults(adapter_name=adapter["name"]),
            )
            config_empty(schemas=schemas, new_config=new_config, source=source)
            config_required(schemas=schemas, new_config=new_config, source=source)

        response_status_hook = self.get_response_status_hook(cnx=cnx_to_add)
        result = self._add(
            connection=new_config,
            adapter_name=adapter["name_raw"],
            instance_name=adapter["node_meta"]["name"],
            instance_id=adapter["node_meta"]["id"],
            is_instances_mode=not adapter["node_meta"]["is_master"],
            save_and_fetch=save_and_fetch,
            active=active,
            connection_label=connection_label,
            response_status_hook=response_status_hook,
            tunnel_id=tunnel_id,
        )
        cnx_new = self.get_by_uuid(
            cnx_uuid=result.id,
            adapter_name=adapter["name"],
            adapter_node=adapter["node_meta"]["name"],
            tunnel=tunnel_id,
        )

        if not result.working and not cnx_new["working"]:
            err = f"Connection was added but had a failure connecting:\n{result}"
            exc = CnxAddError(err)
            exc.result = result
            exc.cnx_new = cnx_new
            raise exc

        return cnx_new

    def test(
        self,
        adapter_name: str,
        adapter_node: Optional[str] = None,
        tunnel: Optional[Union[Tunnel, str]] = None,
        kwargs_config: Optional[dict] = None,
        new_config: Optional[dict] = None,
        parse_config: bool = True,
        **kwargs,
    ) -> dict:
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
            adapter_name (str): name of adapter
            adapter_node (Optional[str], optional): name of node running adapter
            tunnel: tunnel ID or name to use for testing connection
            kwargs_config (Optional[dict], optional): configuration of connection to test
            new_config (Optional[dict], optional): configuration of connection to test
            parse_config (bool, optional): parse configuration for unknowns, requireds, etc
            **kwargs: configuration of connection to test

        Raises:
            CnxTestError: When a connection test fails
            ConfigRequired: When not enough arguments are supplied to test the connection
        """
        new_config = combo_dicts(kwargs_config, new_config, kwargs)
        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node, get_clients=False)
        schemas = self._get(adapter_name=adapter["name_raw"]).schema_cnx
        tunnel_id = self.parent.instances.get_tunnel(value=tunnel, return_id=True)

        cnx_to_test = cnx_from_adapter(adapter)
        cnx_to_test = combo_dicts(cnx_to_test, config=new_config, schemas=schemas)

        if parse_config:
            cnx_str = ", ".join(get_cnx_strs(cnx=cnx_to_test))
            source = f"testing connectivity for connection {cnx_str}"
            new_config = self.build_config(
                cnx_schemas=schemas,
                old_config={},
                new_config=new_config,
                source=source,
                adapter_name=adapter["name"],
                adapter_node=adapter["node_name"],
            )
            config_empty(schemas=schemas, new_config=new_config, source=source)

        cnx_to_test = combo_dicts(cnx_to_test, config=new_config)
        response_status_hook = self.get_response_status_hook(cnx=cnx_to_test)

        return self._test(
            adapter_name=adapter["name_raw"],
            instance=adapter["node_id"],
            connection=new_config,
            tunnel_id=tunnel_id,
            response_status_hook=response_status_hook,
        )

    def test_cnx(self, cnx_test: dict, **kwargs) -> dict:
        """Test a connection for an adapter on a node.

        Args:
            cnx_test: connection fetched previously
        """
        response_status_hook = self.get_response_status_hook(cnx=cnx_test)
        return self._test(
            adapter_name=cnx_test["adapter_name_raw"],
            instance=cnx_test["node_id"],
            connection=cnx_test["config"],
            tunnel_id=cnx_test.get("tunnel_id", None),
            response_status_hook=response_status_hook,
        )

    def update_cnx(
        self,
        cnx_update: dict,
        save_and_fetch: bool = True,
        active: Optional[bool] = None,
        new_node: Optional[str] = None,
        new_tunnel: Optional[Union[Tunnel, str]] = None,
        kwargs_config: Optional[dict] = None,
        new_config: Optional[dict] = None,
        parse_config: bool = True,
        **kwargs,
    ) -> dict:
        """Update a connection for an adapter on a node.

        Args:
            cnx_update: connection fetched previously
            save_and_fetch: perform a fetch when saving, or just save without fetching
            active: set the connection as active or inactive after updating
            new_node: move connection to a new node
            new_tunnel: move connection to a new tunnel ID or name
            kwargs_config: connection args that conflict with this methods signature
            new_config: connection args that conflict with this methods signature
            parse_config: perform api client side parsing of connection args
            **kwargs: configuration of connection to update

        Raises:
            CnxUpdateError: When an error occurs while updating the connection

        Returns:
            dict: updated connection metadata
        """
        node_name = cnx_update["node_name"]
        adapter_name = cnx_update["adapter_name"]
        adapter_old = self.parent.get_by_name(name=adapter_name, node=node_name)
        tunnel_id_old = cnx_update.get("tunnel_id", None)

        if new_node:
            adapter_new = self.parent.get_by_name(name=adapter_name, node=new_node)
        else:
            adapter_new = adapter_old

        if new_tunnel:
            tunnel_id_new = self.parent.instances.get_tunnel(value=new_tunnel, return_id=True)
        else:
            tunnel_id_new = tunnel_id_old

        new_config = combo_dicts(kwargs_config, new_config, kwargs)
        active = active if isinstance(active, bool) else cnx_update["active"]

        cnx_to_update = combo_dicts(
            cnx_update,
            node_id=adapter_new["node_meta"]["id"],
            node_name=adapter_new["node_meta"]["name"],
        )

        if parse_config:
            cnx_str = ", ".join(get_cnx_strs(cnx=cnx_to_update))
            source = f"updating settings for connection {cnx_str}"

            new_config = self.build_config(
                cnx_schemas=cnx_update["schemas"],
                old_config=cnx_update["config"],
                new_config=new_config,
                source=source,
                adapter_name=adapter_new["name"],
                adapter_node=adapter_new["node_meta"]["name"],
            )
            config_empty(schemas=cnx_update["schemas"], new_config=new_config, source=source)
            config_unchanged(
                schemas=cnx_update["schemas"],
                old_config=cnx_update["config"],
                new_config=new_config,
                source=source,
            )

        cnx_to_update = combo_dicts(cnx_update, config=new_config)
        response_status_hook = self.get_response_status_hook(cnx=cnx_to_update)
        result = self._update(
            uuid=cnx_update["uuid"],
            connection=new_config,
            adapter_name=cnx_update["adapter_name_raw"],
            instance_name=adapter_new["node_meta"]["name"],
            instance_id=adapter_new["node_meta"]["id"],
            instance_prev=adapter_old["node_meta"]["id"],
            instance_prev_name=adapter_old["node_meta"]["name"],
            is_instances_mode=not adapter_new["node_meta"]["is_master"],
            tunnel_id=tunnel_id_new,
            save_and_fetch=save_and_fetch,
            active=active,
            connection_label=cnx_update["connection_label"],
            response_status_hook=response_status_hook,
        )

        cnx_new = self.get_by_uuid(
            cnx_uuid=result.id,
            adapter_name=cnx_update["adapter_name"],
            adapter_node=adapter_new["node_meta"]["name"],
            tunnel=tunnel_id_new,
        )

        if not result.working and not cnx_new["working"]:
            err = f"Connection configuration was updated but had a failure connecting:\n{result}"
            exc = CnxUpdateError(err)
            exc.result = result
            exc.cnx_old = cnx_update
            exc.cnx_new = cnx_new
            raise exc

        return cnx_new

    def delete_cnx(self, cnx_delete: dict, delete_entities: bool = False) -> CnxDelete:
        """Delete a connection for an adapter on a node.

        Args:
            cnx_delete (dict): connection fetched previously
            delete_entities (bool, optional): delete all assets fetched by this connection

        Returns:
            CnxDelete: dataclass model containing response
        """
        node = self.parent.instances.get_by_name(name=cnx_delete["node_name"])
        response_status_hook = self.get_response_status_hook(cnx=cnx_delete)
        return self._delete(
            adapter_name=cnx_delete["adapter_name_raw"],
            uuid=cnx_delete["uuid"],
            delete_entities=delete_entities,
            instance_id=cnx_delete["node_id"],
            instance_name=cnx_delete["node_name"],
            is_instances_mode=not node["is_master"],
            response_status_hook=response_status_hook,
        )

    def set_cnx_active(self, cnx: dict, value: bool, save_and_fetch: bool = False) -> dict:
        """Set a connection to active.

        Args:
            cnx (dict): Previously fetched connection object
            value (bool): Set cnx as active or inactive
            save_and_fetch (bool, optional): When saving, perform a fetch as well

        Returns:
            dict: updated cnx object
        """
        node = self.parent.instances.get_by_name(name=cnx["node_name"])
        response_status_hook = self.get_response_status_hook(cnx=cnx)
        result = self._update(
            uuid=cnx["uuid"],
            connection=cnx["config"],
            adapter_name=cnx["adapter_name_raw"],
            instance_name=node["name"],
            instance_id=node["id"],
            instance_prev=node["id"],
            instance_prev_name=node["name"],
            tunnel_id=cnx.get("tunnel_id", None),
            is_instances_mode=not node["is_master"],
            save_and_fetch=save_and_fetch,
            active=value,
            connection_label=cnx["connection_label"],
            response_status_hook=response_status_hook,
        )
        cnx = self.get_by_uuid(
            cnx_uuid=result.id,
            adapter_name=cnx["adapter_name"],
            adapter_node=node["name"],
            tunnel=cnx.get("tunnel_id", None),
        )
        return cnx

    def set_cnx_label(self, cnx: dict, value: str, save_and_fetch: bool = False) -> dict:
        """Set a connections label.

        Args:
            cnx (dict): Previously fetched connection object
            value (bool): label to apply to cnx
            save_and_fetch (bool, optional): When saving, perform a fetch as well

        Returns:
            dict: updated cnx object
        """
        node = self.parent.instances.get_by_name(name=cnx["node_name"])
        response_status_hook = self.get_response_status_hook(cnx=cnx)
        result = self._update(
            uuid=cnx["uuid"],
            connection=cnx["config"],
            adapter_name=cnx["adapter_name_raw"],
            instance_name=node["name"],
            instance_id=node["id"],
            instance_prev=node["id"],
            instance_prev_name=node["name"],
            is_instances_mode=not node["is_master"],
            tunnel_id=cnx.get("tunnel_id", None),
            save_and_fetch=save_and_fetch,
            active=cnx["active"],
            connection_label=value,
            response_status_hook=response_status_hook,
        )
        cnx = self.get_by_uuid(
            cnx_uuid=result.id,
            adapter_name=cnx["adapter_name"],
            adapter_node=node["name"],
            tunnel=cnx.get("tunnel_id", None),
        )
        return cnx

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
                a dictionary that does not have 'uuid' and 'filename' keys,
                or if value is not a file
        """

        def fail(msg):
            sinfo = config_info(schema=schema, value=str(value), source=source)
            msgs = [sinfo, "", f"supplied value: {orig!r}", f"parsed value: {value!r}", msg]
            raise ConfigInvalidValue("\n".join(msgs))

        orig = value
        adapter_name = callbacks["adapter_name"]
        adapter_node = callbacks["adapter_node"]
        field_name = schema["name"]
        value = json_load(obj=value, error=False, load_file=False)
        file_content = None

        if isinstance(value, dict):
            if value.get("uuid") and value.get("filename"):
                return {"uuid": value["uuid"], "filename": value["filename"]}
            fail("supplied dictionary must have uuid and filename keys")

        if isinstance(value, pathlib.Path):
            if not value.is_file():
                fail("supplied pathlib does not exist as a file")
            file_content = value.read_text()

        if isinstance(value, str):
            value = pathify(value)
            if not is_existing_file(value):
                fail("supplied string does not exist as a file")
            file_content = value.read_text()

        if file_content:
            return self.parent.file_upload(
                name=adapter_name,
                field_name=field_name,
                file_name=value.name,
                file_content=file_content,
                node=adapter_node,
            )

        fail("Unable to load contents from file")

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
        tunnel_id: Optional[str] = None,
        response_status_hook: Optional[Callable] = None,
    ) -> CnxCreate:
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
            tunnel_id=tunnel_id,
        )
        return api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            adapter_name=adapter_name,
            response_status_hook=response_status_hook,
        )

    def _test(
        self,
        adapter_name: str,
        instance: str,
        connection: dict,
        tunnel_id: Optional[str] = None,
        response_status_hook: Optional[Callable] = None,
    ) -> dict:
        """Direct API method to add a connection to an adapter.

        Args:
            adapter_name (str): raw name of the adapter i.e. ``aws_adapter``
            instance (str): id of node running adapter
            connection (dict): configuration to test
            tunnel_id (Optional[str], optional): tunnel ID to use
            response_status_hook (Optional[Callable], optional): callable to use when checking
                status codes of response

        Returns:
            dict: containing response
        """
        api_endpoint = ApiEndpoints.adapters.cnx_test
        request_obj = api_endpoint.load_request(
            connection=connection,
            instance=instance,
            tunnel_id=tunnel_id,
        )
        return api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            adapter_name=adapter_name,
            response_status_hook=response_status_hook,
        )

    def _get(self, adapter_name: str) -> Cnxs:
        """Get all connections for a given adapter.

        Args:
            adapter_name (str): name of adapter

        Returns:
            Cnxs: dataclass model containing response
        """
        adapter_name += "" if adapter_name.endswith("_adapter") else "_adapter"
        api_endpoint = ApiEndpoints.adapters.cnx_get
        ret = api_endpoint.perform_request(http=self.auth.http, adapter_name=adapter_name)
        ret.adapter_name = strip_right(obj=adapter_name, fix="_adapter")
        return ret

    def _get_labels(self) -> CnxLabels:
        """Get all connection labels.

        Returns:
            CnxLabels: dataclass model containing response
        """
        return ApiEndpoints.adapters.cnx_get_labels.perform_request(http=self.auth.http)

    def _delete(
        self,
        uuid: str,
        adapter_name: str,
        instance_id: str,
        instance_name: str,
        delete_entities: bool = False,
        is_instances_mode: bool = False,
        response_status_hook: Optional[Callable] = None,
    ) -> CnxDelete:
        """Direct API method to delete a connection from an adapter.

        Args:
            uuid (str): uuid of connection
            adapter_name (str): name of adapter
            instance_id (str): UUID of instance to delete connection from
            instance_name (str): NAME of instance to delete connection from
            delete_entities (bool, optional): delete all assets fetched by this connection
            is_instances_mode (bool, optional): instance_id & instance_name is NOT the Core instance
            response_status_hook (Optional[Callable], optional): callable to use when checking
                status codes of response

        Returns:
            CnxDelete: dataclass model containing response
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
        tunnel_id: Optional[str] = None,
        connection_discovery: Optional[dict] = None,
        is_instances_mode: bool = False,
        save_and_fetch: bool = True,
        active: bool = True,
        connection_label: Optional[str] = None,
        response_status_hook: Optional[Callable] = None,
    ) -> CnxUpdate:
        """Pass.

        Args:
            uuid (str): uuid of connection
            connection (dict): new configuration to apply
            instance_id (str): UUID of instance to move connection to
            instance_name (str): NAME of instance to move connection to
            adapter_name (str): name of adapter
            tunnel_id (Optional[str], optional): tunnel ID to use
            instance_prev (Optional[str], optional): UUID of instance to move connection from
            instance_prev_name (Optional[str], optional): NAME of instance to move connection from
            connection_discovery (Optional[dict], optional): connection specific discovery settings
                to update
            is_instances_mode (bool, optional): instance_id & instance_name is NOT the Core instance
            save_and_fetch (bool, optional): save and fetch the connection, or just save it
            active (bool, optional): set connection as active
            connection_label (Optional[str], optional): label to set on connection
            response_status_hook (Optional[Callable], optional): callable to use when checking
                status codes of response

        Returns:
            CnxModifyResponse: dataclass model containing response
        """
        api_endpoint = ApiEndpoints.adapters.cnx_update
        request_obj = api_endpoint.load_request(
            connection=connection,
            connection_discovery=connection_discovery,
            instance=instance_id,
            instance_name=instance_name,
            instance_prev=instance_prev,
            instance_prev_name=instance_prev_name,
            tunnel_id=tunnel_id,
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

    def get_response_status_hook(self, cnx: dict) -> Callable:
        """Check if the result of updating a connection shows that the connection is gone.

        Args:
            cnx (dict): Connection metadata to use in response hook

        Returns:
            Callable: response status hook
        """

        def response_status_hook(http: Http, response: requests.Response, **kwargs) -> bool:
            """Pass."""
            ret = False
            for error_map in ERROR_MAPS:
                ret = error_map.handle_exc(response=response, cnx=cnx, apiobj=self)
            return ret

        return response_status_hook


@dataclasses.dataclass
class ErrorMap:
    """Mapping container for use in :meth:`Cnx.get_response_status_hook`."""

    response_regexes: List[str]
    """List of regexes that if they match response body, will throw :attr:`exc`"""

    err: str
    """Error string to include in exception if :attr:`response_regexes` match."""

    exc: Type[Exception]
    """Exception class to throw if :attr:`response_regexes` match."""

    endpoint_regexes: List[str] = dataclasses.field(default_factory=list)
    """List of regexes that if they match request URL, will check :attr:`response_regexes`."""

    with_schemas: bool = True
    """Include connection configuration schemas in error output."""

    with_config: bool = True
    """Include connection configuration in error output."""

    with_cnxs: bool = True
    """Include all connections for adapter in question in error output."""

    skip_status: bool = False
    """Skip the rest of the built in status checks."""

    def __post_init__(self):
        """Post init dataclass setup."""
        self.response_regexes = [re.compile(x, re.I) for x in listify(self.response_regexes)]
        self.endpoint_regexes = [re.compile(x, re.I) for x in listify(self.endpoint_regexes)]

    def is_response_error(self, response: requests.Response) -> bool:
        """Check if response matches :attr:`endpoint_regexes` and :attr:`response_regexes`.

        Args:
            response (requests.Response): response object to check

        Returns:
            bool: if response matches this error map
        """

        def any_match(regexes, value):
            return any([x.search(value) for x in listify(regexes)])

        if self.endpoint_regexes and not any_match(
            self.endpoint_regexes, response.url
        ):  # pragma: no cover
            return False

        if any_match(self.response_regexes, response.text):
            return True

        return False

    def handle_exc(self, response: requests.Response, cnx: dict, apiobj: Cnx) -> bool:
        """Handle raising an exception if :meth:`is_response_error`.

        Args:
            response (requests.Response): response object to check
            cnx (dict): connection metadata
            apiobj (Cnx): API model to use to fetch connections

        Returns:
            bool: return :attr:`skip_status`

        Raises:
            Exception: of type :attr:`exc`
        """
        if self.is_response_error(response=response):
            cnx_strs = get_cnx_strs(
                cnx=cnx, with_schemas=self.with_schemas, with_config=self.with_config
            )

            errs = [self.err, "", *cnx_strs]
            err = "\n".join(errs)

            if self.with_cnxs:
                cnxs = apiobj.get_by_adapter(
                    adapter_name=cnx["adapter_name"], adapter_node=cnx["node_name"]
                )
                err = tablize_cnxs(cnxs=cnxs, err=err)

            exc = self.exc(err)
            exc.cnx = cnx
            raise exc

        return self.skip_status


CNX_STRS: dict = {
    "adapter_name": "Adapter Name: {adapter_name!r}",
    "node_name": "Instance name: {node_name!r}",
    "node_id": "Instance ID: {node_id!r}",
    "id": "Connection ID: {node_id!r}",
    "uuid": "Connection UUID: {node_id!r}",
    "active": "Is active: {active}",
    "status": "Status: {status}",
}


def get_cnx_strs(cnx: dict, with_config: bool = False, with_schemas: bool = False) -> List[str]:
    """Build a string with details about a connection.

    Args:
        cnx (dict): connection to build string for
        with_config (bool, optional): include connection config in output
        with_schemas (bool, optional): include connection config schemas in output

    Returns:
        List[str]: connection details
    """
    ret = [v.format(**cnx) for k, v in CNX_STRS.items() if k in cnx]

    if with_config and "config" in cnx:
        ret += ["Configuration:", f"{json_dump(cnx['config'])}"]

    if with_schemas and "schemas" in cnx:
        ret += ["Configuration Schema:", tablize_schemas(schemas=cnx["schemas"])]
    return ret


def cnx_from_adapter(adapter: dict) -> dict:
    """Build a base dict for a connection with details from an adapter metadata dict.

    Args:
        adapter (dict): adapter to get details from

    Returns:
        dict: base dict for connection
    """
    ret = {}
    ret["adapter_name"] = adapter["name"]
    ret["adapter_name_raw"] = adapter["name_raw"]
    ret["node_name"] = adapter["node_name"]
    ret["node_id"] = adapter["node_id"]
    return ret


# NB: Could be dataclass
ERROR_MAPS: List[ErrorMap] = [
    ErrorMap(
        response_regexes="type.*InvalidId",
        exc=CnxError,
        err="Invalid instance ID or instance name",
    ),
    ErrorMap(
        response_regexes="type.*JSONDecodeError",
        exc=ConfigRequired,
        err="Connection configuration missing required keys",
    ),
    ErrorMap(
        response_regexes="Adapter name and connection data are required",
        exc=ConfigRequired,
        err="Connection configuration missing required keys",
    ),
    ErrorMap(
        response_regexes="invalid client",
        with_cnxs=False,
        exc=ConfigRequired,
        err="Connection configuration missing required keys",
    ),
    ErrorMap(
        response_regexes="Adapter.*not found",
        with_cnxs=False,
        exc=CnxError,
        err="Invalid adapter name",
    ),
    ErrorMap(
        response_regexes="Server is already gone",
        exc=CnxGoneError,
        err="Connection is gone - updated or deleted by someone else!",
    ),
    ErrorMap(
        response_regexes="Client is not reachable",
        with_cnxs=False,
        exc=CnxTestError,
        err="Connection test failed",
    ),
]
