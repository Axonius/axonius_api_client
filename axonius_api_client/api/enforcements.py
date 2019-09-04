# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import warnings

from .. import exceptions, tools
from . import mixins, routers, users_devices


class Actions(mixins.Child):
    """Action related API methods.

    Notes:
        The REST API will need to be updated to allow more power in this library.
        Until then, this class should be considered **BETA**.

    """

    @property
    def _router(self):
        """Router for this API client.

        Returns:
            :obj:`axonius_api_client.api.routers.Router`

        """
        return routers.ApiV1.actions

    # sort of pointless
    def _get(self):
        """Get all actions.

        Returns:
            :obj:`list` of :obj:`str`

        """
        return self._parent._request(method="get", path=self._router.root)

    # FUTURE:
    # this returns nothing...
    # AND no action shows up in GUI for dvc
    # AND no task shows up in EC
    def _shell(self, name, ids, command):
        """Run an action.

        Args:
            name (:obj:`str`):
                Name of action to run.
            ids (:obj:`list` of :obj:`str`):
                Internal axonius IDs of device to run action against.
            command (:obj:`str`):
                Command to run.

        Returns:
            :obj:`object`

        """
        data = {}
        data["action_name"] = name
        data["internal_axon_ids"] = ids
        data["command"] = command
        return self._parent._request(method="post", path=self._router.shell, json=data)

    # FUTURE: Figure out return.
    def _deploy(self, name, ids, binary_uuid, binary_filename, params=None):
        """Deploy an action.

        Args:
            name (:obj:`str`):
                Name of action to deploy.
            ids (:obj:`list` of :obj:`str`):
                Internal axonius IDs of device to deploy action against.
            binary_uuid (:obj:`str`):
                UUID of binary to use in deployment.
            binary_filename (:obj:`str`):
                Filename of binary to use in deployment.
            params (:obj:`str`, optional):
                Defaults to: None.

        Returns:
            :obj:`object`

        """
        data = {}
        data["action_name"] = name
        data["internal_axon_ids"] = ids
        data["binary"] = {}
        data["binary"]["filename"] = binary_filename
        data["binary"]["uuid"] = binary_uuid
        if params:
            data["params"] = params
        return self._parent._request(method="post", path=self._router.deploy, json=data)

    def _upload_file(self, binary, filename):
        """Upload a file to the system for use in deployment.

        Args:
            binary (:obj:`io.BytesIO`):
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
        return self._parent._request(
            method="post", path=self._router.upload_file, data=data, files=files
        )


class Enforcements(mixins.Model, mixins.Mixins):
    """Enforcement related API methods.

    Notes:
        The REST API will need to be updated to allow more power in this library.
        Until then, this class should be considered **BETA**.

    """

    def _init(self, auth, **kwargs):
        """Pass."""
        # cross ref
        self.users = users_devices.Users(auth=auth, **kwargs)
        self.devices = users_devices.Devices(auth=auth, **kwargs)

        # children
        self.actions = Actions(parent=self)

        msg = "This module is considered **BETA** status! Here be dragons..."
        warnings.warn(msg, exceptions.ApiWarning)

        super(Enforcements, self)._init(auth=auth, **kwargs)

    @property
    def _router(self):
        """Router for this API client.

        Returns:
            :obj:`axonius_api_client.api.routers.Router`

        """
        return routers.ApiV1.alerts

    def _delete(self, ids):
        """Delete objects by internal axonius IDs.

        Args:
            ids (:obj:`list` of :obj:`str`):
                List of internal axonius IDs of objects to delete.

        Returns:
            None

        """
        return self._request(method="delete", path=self._router.root, json=ids)

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
        return self._request(method="put", path=self._router.root, json=data)

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

        response = self._request(method="get", path=self._router.root, params=params)
        return response["assets"]

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

        if tools.is_type.list(found):
            ids = [x["uuid"] for x in found]
        else:
            ids = [found["uuid"]]

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
                value=query, value_type="query", object_type="Alert", exc=None
            )

        return found[0] if only1 else found
