# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import exceptions
from . import models


class ApiUsers(models.ApiVersion1, models.ApiBase, models.UserDeviceBase):
    """User related API methods."""

    @property
    def _obj_route(self):
        """Get the object route.

        Returns:
            :obj:`str`

        """
        return "users"

    @property
    def _default_fields(self):
        """Fields to set as default for methods with **fields.

        Returns:
            :obj:`dict`

        """
        return {
            "generic": [
                "adapters",
                "labels",
                "specific_data.data.username",
                "specific_data.data.last_seen",
            ]
        }

    @property
    def _name_field(self):
        """Field name to use in :meth:`axonius_api_client.UserDeviceBase.get_by_name`.

        Returns:
            :obj:`str`

        """
        return "specific_data.data.username"


class ApiDevices(models.ApiVersion1, models.ApiBase, models.UserDeviceBase):
    """Device related API methods."""

    @property
    def _obj_route(self):
        """Get the object route.

        Returns:
            :obj:`str`

        """
        return "devices"

    @property
    def _default_fields(self):
        """Fields to set as default for methods with **fields.

        Returns:
            :obj:`dict`

        """
        return {
            "generic": [
                "adapters",
                "labels",
                "specific_data.data.hostname",
                "specific_data.data.network_interfaces.ips",
                "specific_data.data.last_seen",
            ]
        }

    @property
    def _name_field(self):
        """Field name to use in :meth:`axonius_api_client.UserDeviceBase.get_by_name`.

        Returns:
            :obj:`str`

        """
        return "specific_data.data.hostname"


class ApiActions(models.ApiVersion1, models.ApiBase):
    """Action related API methods.

    Notes:
        The REST API will need to be updated to allow more power in this library.
        Until then, this class should be considered **BETA**.

    """

    @property
    def _obj_route(self):
        """Get the object route.

        Returns:
            :obj:`str`

        """
        return "actions"

    def get(self):
        """Get all actions.

        Returns:
            :obj:`list` of :obj:`str`

        """
        return self._request(method="get", obj_route="actions", route="")

    def run(self, name, ids, command):
        """Run an action.

        Args:
            name (:obj:`str`):
                Name of action to run.
            ids (:obj:`list` of :obj`str`):
                Internal axonius IDs of device to run action against.
            command (:obj:`str`):
                command to run.

        """
        data = {}
        data["action_name"] = name
        data["internal_axon_ids"] = ids
        data["command"] = command
        return self._request(method="post", route="shell", json=data)

    def deploy(self, name, ids, binary_uuid, binary_filename, params=None):
        """Deploy an action.

        Args:
            name (:obj:`str`):
                Name of action to deploy.
            ids (:obj:`list` of :obj`str`):
                Internal axonius IDs of device to deploy action against.
            binary_uuid (:obj:`str`):
                UUID of binary to use in deployment.
            binary_filename (:obj:`str`):
                Filename of binary to use in deployment.
            params (:obj:`str`, optional):
                FUTURE: Figure this out.

                Defaults to: None.

        Returns:
            FUTURE: Figure this out.

        """
        data = {}
        data["action_name"] = name
        data["internal_axon_ids"] = ids
        data["binary"] = {}
        data["binary"]["filename"] = binary_filename
        data["binary"]["uuid"] = binary_uuid
        if params:
            data["params"] = params
        return self._request(method="post", route="deploy", json=data)

    def upload_file(self, binary, filename):
        """Upload a file to the system for use in deployment.

        Args:
            binary (:obj:`io.BinaryIO`):
                Binary bits of file to upload.
            filename (:obj:`str`):
                Name of file to upload.

        Returns:
            :obj:`str`: UUID of uploaded file.

        """
        data = {}
        data["field_name"] = "binary"
        files = {}
        files["userfile"] = (filename, binary)
        return self._request(method="post", route="upload_file", data=data, files=files)


class ApiAdapters(models.ApiVersion1, models.ApiBase):
    """Adapter related API methods.

    Notes:
        The REST API will need to be updated to allow more power in this library.
        Until then, this class should be considered **BETA**.

    """

    @property
    def _obj_route(self):
        """Get the object route.

        Returns:
            :obj:`str`

        """
        return "alerts"

    def get(self):
        """Get all adapters.

        Returns:
            FUTURE: Figure this out.

        """
        return self._request(method="get", route="")

    # FUTURE: public method
    def _check_client(self, name, config, node_id):
        """Check connectivity for a client of an adapter.

        Args:
            name (:obj:`str`):
                Name of adapter to check client connectivity of.
            config (:obj:`dict`):
                Client configuration.
            node_id (:obj:`str`):
                Node ID.

        Returns:
            FUTURE: Figure this out.

        """
        data = {}
        data.update(config)
        data["instanceName"] = node_id
        data["oldInstanceName"] = node_id
        route = "{name}/clients".format(name=name)
        return self._request(method="post", route=route, json=data)

    # FUTURE: public method
    def _add_client(self, name, config, node_id):
        """Add a client to an adapter.

        Args:
            name (:obj:`str`):
                Name of adapter to add client to.
            config (:obj:`dict`):
                Client configuration.
            node_id (:obj:`str`):
                Node ID.

        Returns:
            FUTURE: Figure this out.

        """
        data = {}
        data.update(config)
        data["instanceName"] = node_id
        route = "{name}/clients".format(name=name)
        return self._request(method="put", route=route, json=data)

    # FUTURE: public method
    def _delete_client(self, name, id, node_id):
        """Delete a client from an adapter.

        Args:
            name (:obj:`str`):
                Name of adapter to delete client from.
            id (:obj:`str`):
                ID of client to remove.
            node_id (:obj:`str`):
                Node ID.

        Returns:
            FUTURE: Figure this out.

        """
        data = {}
        data["instanceName"] = node_id
        route = "{name}/clients/{id}".format(name=name, id=id)
        return self._request(method="delete", route=route, json=data)


class ApiEnforcements(models.ApiVersion1, models.ApiBase):
    """Enforcement related API methods.

    Notes:
        The REST API will need to be updated to allow more power in this library.
        Until then, this class should be considered **BETA**.

    """

    @property
    def _obj_route(self):
        """Get the object route.

        Returns:
            :obj:`str`

        """
        return "alerts"

    def _delete(self, ids):
        """Delete objects by internal axonius IDs.

        Args:
            ids (:obj:`list` of :obj:`str`):
                List of internal axonius IDs of objects to delete.

        Returns:
            None

        """
        return self._request(method="get", route="", json=ids)

    # FUTURE: public method
    def _create(self, name, main, success=None, failure=None, post=None, triggers=None):
        """Create an enforcement.

        Args:
            name (:obj:`str`):
                Name of new enforcement to create.
            main (:obj:`dict`):
                Main action to run for this enforcement.
            success (:obj:`list` of :obj:`dict`, optional):
                Actions to run on success.

                Defaults to: None.
            failure (:obj:`list` of :obj:`dict`, optional):
                Actions to run on failure.

                Defaults to: None.
            post (:obj:`list` of :obj:`dict`, optional):
                Actions to run on post.

                Defaults to: None.
            triggers (:obj:`list` of :obj:`dict`, optional):
                Triggers for this enforcement.

                Defaults to: None.

        Notes:
            This will get a public create method once the REST API server has been
            updated to expose /enforcements/actions, /api/enforcements/actions/saved,
            and others.

        Returns:
            :obj:`str`: ID of newly created object.

        """
        data = {}
        data["name"] = name
        data["actions"] = {}
        data["actions"]["main"] = main
        data["actions"]["success"] = success or []
        data["actions"]["failure"] = success or []
        data["actions"]["post"] = success or []
        data["triggers"] = triggers or []
        return self._request(method="put", route="", json=data)

    def get(self, query=None, row_start=0, page_size=0):
        """Get a page for a given query.

        Args:
            query (:obj:`str`, optional):
                Query to filter rows to return. This is NOT a query built by
                the Query Wizard in the GUI. This is something else. See
                :meth:`get_by_name` for an example query. Empty
                query will return all rows.

                Defaults to: None.
            row_start (:obj:`int`, optional):
                If not 0, skip N rows in the return.

                Defaults to: 0.
            page_size (:obj:`int`, optional):
                If not 0, include N rows in the return.

                Defaults to: 0.

        Returns:
            :obj:`dict`

        """
        params = {}

        if page_size:
            params["limit"] = page_size

        if row_start:
            params["skip"] = row_start

        if query:
            params["filter"] = query

        return self._request(method="get", route="", params=params)["assets"]

    def delete_by_name(self, name, regex=False, only1=True):
        """Delete an enforcement by name.

        Args:
            name (:obj:`str`):
                Name of object to delete.
            regex (:obj:`bool`, optional):
                Search for name using regex.

                Defaults to: False.
            only1 (:obj:`bool`, optional):
                Only allow one match to name.

                Defaults to: True.

        Returns:
            :obj:`str`: empty string

        """
        found = self.get_by_name(name=name, regex=regex, only1=True)
        ids = [x["uuid"] for x in found] if isinstance(found, list) else [found["uuid"]]
        return self._delete(ids=ids)

    def get_by_name(self, name, regex=True, only1=False):
        """Get enforcements by name.

        Args:
            name (:obj:`str`):
                Name of object to get.
            regex (:obj:`bool`, optional):
                Search for name using regex.

                Defaults to: True.
            only1 (:obj:`bool`, optional):
                Only allow one match to name.

                Defaults to: True.

        Raises:
            :exc:`exceptions.ObjectNotFound`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        if regex:
            query = 'name == regex("{name}", "i")'.format(name=name)
        else:
            query = 'name == "{name}"'.format(name=name)

        found = self.get(query=query)

        if not found or (len(found) > 1 and only1):
            raise exceptions.ObjectNotFound(
                value=query, value_type="query", object_type="Alert"
            )

        return found[0] if only1 else found
