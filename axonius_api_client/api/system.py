# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import warnings

from .. import constants, exceptions
from . import mixins, routers


class System(mixins.Model, mixins.Mixins):
    """System methods."""

    @property
    def _router(self):
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        return routers.ApiV1.system

    @property
    def instances(self):
        """Get instances child object.

        Returns:
            :obj:`Instances`
        """
        if not hasattr(self, "_instances"):
            self._instances = Instances(parent=self)
        return self._instances

    @property
    def settings(self):
        """Get settings child object.

        Returns:
            :obj:`Settings`
        """
        if not hasattr(self, "_settings"):
            self._settings = Settings(parent=self)
        return self._settings

    @property
    def meta(self):
        """Get meta child object.

        Returns:
            :obj:`Meta`
        """
        if not hasattr(self, "_meta"):
            self._meta = Meta(parent=self)
        return self._meta

    @property
    def discover(self):
        """Get discover child object.

        Returns:
            :obj:`Discover`
        """
        if not hasattr(self, "_discover"):
            self._discover = Discover(parent=self)
        return self._discover

    @property
    def users(self):
        """Get users child object.

        Returns:
            :obj:`Users`
        """
        if not hasattr(self, "_users"):
            self._users = Users(parent=self)
        return self._users

    @property
    def roles(self):
        """Get roles child object.

        Returns:
            :obj:`Roles`
        """
        if not hasattr(self, "_roles"):
            self._roles = Roles(parent=self)
        return self._roles

    # TODO
    """
    def _request, self._has_system_about(), super()
    def _has_system_about():
        try:
            self.meta.about()
        except:
            raise "Ask apiclient@axonius.com to enable support for this method!"
    """


class Discover(mixins.Child):
    """Child API model for working with discovery cycles."""

    def _lifecycle(self):
        """Direct API method to get discovery cycle metadata.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        path = self._router.discover_lifecycle
        return self._request(method="get", path=path)

    def _start(self):
        """Direct API method to start a discovery cycle."""
        path = self._router.discover_start
        return self._request(method="post", path=path)

    def _stop(self):
        """Direct API method to stop a discovery cycle.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        path = self._router.discover_stop
        return self._request(method="post", path=path)

    def lifecycle(self):
        """Get lifecycle metadata.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        return self._lifecycle()

    @property
    def is_running(self):
        """Check if discovery cycle is running.

        Returns:
            :obj:`bool`: if discovery cycle is running
        """
        return not self.lifecycle()["status"] == "done"

    def start(self):
        """Start a discovery cycle if one is not running.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        if not self.is_running:
            self._start()
        return self.lifecycle()

    def stop(self):
        """Stop a discovery cycle if one is running.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        if self.is_running:
            self._stop()
        return self.lifecycle()


class Instances(mixins.Child):
    """Child API model for working with instances."""

    def _init(self, parent):
        """Post init method for subclasses to use for extra setup.

        Args:
            parent (:obj:`.api.mixins.Model`): parent API model of this child
        """
        super(Instances, self)._init(parent=parent)
        warnings.warn(exceptions.BetaWarning(obj=self))

    def _get(self):
        """Direct API method to get instances.

        Returns:
            :obj:`dict`: instances
        """
        """Example return
        {
            "connection_data": {
                "host": "<axonius-hostname>",
                "key": "***REMOVED***"
            },
            "instances": [
                {
                    "hostname": "builds-vm-jim-2-15-b-1581114965-000",
                    "ips": [
                        "***REMOVED***"
                    ],
                    "last_seen": "Sun, 09 Feb 2020 22:19:22 GMT",
                    "node_id": "a7afe3af5d05428dbecc55704fc7e3ea",
                    "node_name": "Master",
                    "node_user_password": "",
                    "status": "Activated",
                    "tags": {}
                }
            ]
        }
        """
        return self._request(method="get", path=self._router.instances)

    def _delete(self, node_id):  # pragma: no cover
        """Pass."""
        data = {"nodeIds": node_id}
        path = self._router.instances
        return self._request(method="delete", path=path, json=data)

    def _update(self, node_id, node_name, hostname):  # pragma: no cover
        """Direct API method to update an instance.

        Args:
            node_id (:obj:`str`): node id of instance
            node_name (:obj:`str`): node name of instance
            hostname (:obj:`str`): hostname of instance

        Returns:
            :obj:`dict`: updated instance
        """
        """Example return

        {
            "nodeIds": "a7afe3af5d05428dbecc55704fc7e3ea",
            "node_name": "Masterx",
            "hostname": "builds-vm-jim-2-15-b-1581114965-000"
        }
        """
        data = {"nodeIds": node_id, "node_name": node_name, "hostname": hostname}
        path = self._router.instances
        return self._request(method="update", path=path, json=data)

    def get(self):
        """Get instances.

        Returns:
            :obj:`dict`: instances
        """
        return self._get()


class Meta(mixins.Child):
    """Child API model for working with instance metadata."""

    def _init(self, parent):
        """Post init method for subclasses to use for extra setup.

        Args:
            parent (:obj:`.api.mixins.Model`): parent API model of this child
        """
        super(Meta, self)._init(parent=parent)

    def _about(self):
        """Direct API method to get the About page.

        Returns:
            :obj:`dict`: about page metadata
        """
        path = self._router.meta_about
        return self._request(method="get", path=path)

    def _historical_sizes(self):
        """Direct API method to get the metadata about disk usage.

        Returns:
            :obj:`dict`: disk usage metadata
        """
        path = self._router.meta_historical_sizes
        return self._request(method="get", path=path)

    def about(self):
        """Get about page metadata.

        Returns:
            :obj:`dict`: about page metadata
        """
        return self._about()

    def historical_sizes(self):
        """Get disk usage metadata.

        Returns:
            :obj:`dict`: disk usage metadata
        """
        return self._historical_sizes()


class Settings(mixins.Child):
    """Child API model for working with system settings."""

    def _init(self, parent):
        """Post init method for subclasses to use for extra setup.

        Args:
            parent (:obj:`.api.mixins.Model`): parent API model of this child
        """
        super(Settings, self)._init(parent=parent)
        warnings.warn(exceptions.BetaWarning(obj=self))

    @property
    def core(self):
        """Get SettingsCore child object.

        Returns:
            :obj:`SettingsCore`
        """
        if not hasattr(self, "_settings_core"):
            self._settings_core = SettingsCore(parent=self)
        return self._settings_core

    @property
    def gui(self):
        """Get SettingsGui child object.

        Returns:
            :obj:`SettingsGui`
        """
        if not hasattr(self, "_settings_gui"):
            self._settings_gui = SettingsGui(parent=self)
        return self._settings_gui

    @property
    def lifecycle(self):
        """Get SettingsLifecycle child object.

        Returns:
            :obj:`SettingsLifecycle`
        """
        if not hasattr(self, "_settings_lifecycle"):
            self._settings_lifecycle = SettingsLifecycle(parent=self)
        return self._settings_lifecycle


class SettingsChild(mixins.Child):
    """Child API object to work with system settings."""

    def _get(self):
        """Direct API method to get the current system settings.

        Returns:
            :obj:`dict`: current system settings
        """
        return self._request(method="get", path=self._router_path)

    def _update(self, config):
        """Direct API method to update the system settings."""
        return self._request(method="post", path=self._router_path, json=config)

    def get(self):
        """Get the current system settings.

        Returns:
            :obj:`dict`: current system settings
        """
        return self._get()["config"]

    def update(self, config):
        """Update the system settings.

        Returns:
            :obj:`dict`: updated system settings
        """
        self._update(config=config)
        return self.get()


class SettingsCore(SettingsChild):
    """Child API object to work with System Global Settings."""

    @property
    def _router_path(self):
        """Route path for this setting object."""
        return self._parent._router.settings_core

    '''
    @property
    def aggregation(self):
        """Get Aggregation child object.

        Returns:
            :obj:`Aggregation`
        """
        if not hasattr(self, "_aggregation"):
            self._aggregation = Aggregation(parent=self)
        return self._aggregation

    '''


class SettingsGui(SettingsChild):
    """Child API object to work with GUI Global Settings."""

    @property
    def _router_path(self):
        """Route path for this setting object."""
        return self._parent._router.settings_gui


class SettingsLifecycle(SettingsChild):
    """Child API object to work with Lifecycle Global Settings."""

    @property
    def _router_path(self):
        """Route path for this setting object."""
        return self._parent._router.settings_lifecycle


'''
class Aggregation(mixins.Child):
    """Aggregation settings under Global Settings in Administrative settings."""

    @property
    def _subkey(self):
        """Pass."""
        return "aggregation_settings"

    def get(self):
        """Pass."""
        return self._parent.get()[self._subkey]

    def max_workers(self, value):
        """Update Maximum adapters to execute asynchronously.

        Found under: Administrative Settings > Global Settings >
        Aggregation Settings > Maximum adapters to execute asynchronously.

        Args:
            value (int)

        Returns:
            dict: aggregation settings with updated value
        """
        tools.val_type(value=value, types=constants.INT)
        settings = self._parent.get()
        settings[self._subkey]["max_workers"] = value
        self._parent.update(config=settings)
        return self.get()

    def socket_read_timeout(self, value):
        """Update Maximum adapters to execute asynchronously.

        Found under: Administrative Settings > Global Settings >
        Aggregation Settings > Socket read-timeout in seconds.

        Args:
            value (int)

        Returns:
            dict: aggregation settings with updated value
        """
        tools.val_type(value=value, types=constants.INT)
        settings = self._parent.get()
        settings[self._subkey]["socket_read_timeout"] = value
        self._parent.update(config=settings)
        return self.get()
'''


class Roles(mixins.Child):
    """Child API object to work with Roles."""

    def _get_default(self):
        """Direct API method to get the current default role for external users.

        Returns:
            :obj:`str`: current default role for external users
        """
        path = self._router.roles_default
        return self._request(method="get", path=path, error_json_invalid=False)

    def _set_default(self, name):
        """Direct API method to set the default role for external users.

        Args:
            name (:obj:`str`): name of role to set as the default role for external users
        """
        data = {"name": name}
        path = self._router.roles_default
        return self._request(method="post", path=path, json=data)

    def _get(self):
        """Direct API method to get known roles.

        Returns:
            :obj:`list` of :obj:`str`: known roles
        """
        path = self._router.roles
        return self._request(method="get", path=path)

    def _add(self, name, permissions):
        """Direct API method to add a role.

        Args:
            name (:obj:`str`): name of new role
            permissions (:obj:`dict`): permissions for new role
        """
        data = {"name": name, "permissions": permissions}
        path = self._router.roles
        return self._request(method="put", path=path, json=data)

    def _update(self, name, permissions):
        """Direct API method to update a roles permissions.

        Args:
            name (:obj:`str`): name of role to update
            permissions (:obj:`dict`): permissions to update on new role
        """
        data = {"name": name, "permissions": permissions}
        path = self._router.roles
        return self._request(
            method="post", path=path, json=data, error_json_invalid=False
        )

    def _delete(self, name):
        """Direct API method to delete a role.

        Args:
            name (:obj:`str`): name of role to delete
        """
        data = {"name": name}
        path = self._router.roles
        return self._request(
            method="delete", path=path, json=data, error_json_invalid=False
        )

    def set_default(self, name):
        """Set the default role for external users.

        Args:
            name (:obj:`str`): name of role to set as the default role for external users

        Returns:
            :obj:`dict`: metadata of default role that was set as new default
        """
        role = self.get(name=name)
        self._set_default(name=name)
        return role

    def get_default(self):
        """Get the default role for external users.

        Returns:
            :obj:`dict`: metadata of default role
        """
        name = self._get_default()
        return self.get(name=name)

    def get(self, name=None):
        """Pass."""  # XXX
        roles = self._get()
        if name:
            role_names = self.get_names(roles=roles)
            if name not in role_names:
                msg = "Role not found {n!r}, valid roles: {vr}"
                msg = msg.format(n=name, vr=", ".join(role_names))
                raise exceptions.ApiError(msg)
            return [x for x in roles if x["name"] == name][0]
        return roles

    def get_names(self, roles=None):
        """Pass."""
        roles = roles if roles else self.get()
        return [x["name"] for x in roles]

    def _check_valid_perm(self, name, value):
        """Pass."""
        if value not in constants.VALID_PERMS:
            msg = "Invalid permission {p!r} for {n!r} - Must be one of {vp}"
            msg = msg.format(p=value, n=name, vp=", ".join(constants.VALID_PERMS))
            raise exceptions.ApiError(msg)

    def _check_valid_perms(
        self,
        adapters,
        dashboard,
        devices,
        enforcements,
        instances,
        reports,
        settings,
        users,
    ):
        """Pass."""
        self._check_valid_perm(name="adapters", value=adapters)
        self._check_valid_perm(name="dashboard", value=dashboard)
        self._check_valid_perm(name="devices", value=devices)
        self._check_valid_perm(name="enforcements", value=enforcements)
        self._check_valid_perm(name="instances", value=instances)
        self._check_valid_perm(name="reports", value=reports)
        self._check_valid_perm(name="settings", value=settings)
        self._check_valid_perm(name="users", value=users)

        return {
            "Adapters": adapters,
            "Dashboard": dashboard,
            "Devices": devices,
            "Enforcements": enforcements,
            "Instances": instances,
            "Reports": reports,
            "Settings": settings,
            "Users": users,
        }

    def add(
        self,
        name,
        adapters=constants.DEFAULT_PERM,
        dashboard=constants.DEFAULT_PERM,
        devices=constants.DEFAULT_PERM,
        enforcements=constants.DEFAULT_PERM,
        instances=constants.DEFAULT_PERM,
        reports=constants.DEFAULT_PERM,
        settings=constants.DEFAULT_PERM,
        users=constants.DEFAULT_PERM,
    ):
        """Pass."""
        names = self.get_names()
        if name in names:
            msg = "Role named {n!r} already exists"
            msg = msg.format(n=name)
            raise exceptions.ApiError(msg)

        permissions = self._check_valid_perms(
            adapters=adapters,
            dashboard=dashboard,
            devices=devices,
            enforcements=enforcements,
            instances=instances,
            reports=reports,
            settings=settings,
            users=users,
        )
        self._add(name=name, permissions=permissions)
        return self.get(name=name)

    def update(
        self,
        name,
        adapters=constants.DEFAULT_PERM,
        dashboard=constants.DEFAULT_PERM,
        devices=constants.DEFAULT_PERM,
        enforcements=constants.DEFAULT_PERM,
        instances=constants.DEFAULT_PERM,
        reports=constants.DEFAULT_PERM,
        settings=constants.DEFAULT_PERM,
        users=constants.DEFAULT_PERM,
    ):
        """Pass."""
        names = self.get_names()
        if name not in names:
            msg = "Role named {n!r} does not exist"
            msg = msg.format(n=name)
            raise exceptions.ApiError(msg)

        permissions = self._check_valid_perms(
            adapters=adapters,
            dashboard=dashboard,
            devices=devices,
            enforcements=enforcements,
            instances=instances,
            reports=reports,
            settings=settings,
            users=users,
        )
        self._update(name=name, permissions=permissions)
        return self.get(name=name)

    def delete(self, name):
        """Pass."""
        names = self.get_names()
        if name not in names:
            msg = "Role named {n!r} does not exist"
            msg = msg.format(n=name)
            raise exceptions.ApiError(msg)
        self._delete(name=name)
        return self.get()


class Users(mixins.Child):
    """User Role controls."""

    def _get(self, limit=None, skip=None):
        """Pass."""
        data = {}
        if limit is not None:
            data["limit"] = limit
        if skip is not None:
            data["skip"] = skip
        path = self._router.users
        return self._request(method="get", path=path, params=data)

    def _add(self, name, password, firstname="", lastname="", rolename=""):
        """Pass."""
        data = {
            "user_name": name,
            "password": password,
            "first_name": firstname,
            "last_name": lastname,
            "role_name": rolename,
        }
        path = self._router.users
        return self._request(method="put", path=path, json=data)

    def _delete(self, uuid):
        """Pass."""
        path = self._router.user.format(uuid=uuid)
        return self._request(method="delete", path=path)

    def _update(self, uuid, firstname, lastname, password):
        """Pass."""
        data = {}
        if firstname:
            data["first_name"] = firstname
        if lastname:
            data["last_name"] = lastname
        if password:
            data["password"] = password
        path = self._router.user.format(uuid=uuid)
        return self._request(
            method="post", path=path, json=data, error_json_invalid=False
        )

    def _update_role(self, uuid, rolename, permissions):
        """Pass."""
        data = {}
        data["role_name"] = rolename
        data["permissions"] = permissions
        path = self._router.user_role.format(uuid=uuid)
        return self._request(
            method="post", path=path, json=data, error_json_invalid=False
        )

    def add(self, name, password, firstname="", lastname="", rolename=""):
        """Pass."""
        if rolename:
            self._parent.roles.get(name=rolename)

        names = self.get_names()
        if name in names:
            msg = "User named {n!r} already exists"
            msg = msg.format(n=name)
            raise exceptions.ApiError(msg)

        self._add(
            name=name,
            password=password,
            firstname=firstname,
            lastname=lastname,
            rolename=rolename,
        )
        return self.get(name=name)

    def get(self, name=None):
        """Pass."""
        users = self._get()
        if name:
            names = self.get_names(users=users)
            if name not in names:
                msg = "User not found {n!r}, valid users: {vr}"
                msg = msg.format(n=name, vr=", ".join(names))
                raise exceptions.ApiError(msg)
            return [x for x in users if x["user_name"] == name][0]
        return users

    def get_names(self, users=None):
        """Pass."""
        users = users if users else self.get()
        return [x["user_name"] for x in users]

    def update(self, name, firstname=None, lastname=None, password=None):
        """Pass."""
        if not any([firstname, lastname, password]):
            msg = "Must supply at least one of: {req!r}"
            msg = msg.format(req=", ".format("firstname", "lastname", "password"))
            raise exceptions.ApiError(msg)

        user = self.get(name=name)
        uuid = user["uuid"]

        self._update(
            uuid=uuid, firstname=firstname, lastname=lastname, password=password,
        )
        return self.get(name=name)

    def update_role(self, name, rolename):
        """Pass."""
        user = self.get(name=name)
        role = self._parent.roles.get(name=rolename)

        uuid = user["uuid"]
        rolename = role["name"]
        permissions = role["permissions"]

        self._update_role(uuid=uuid, rolename=rolename, permissions=permissions)
        return self.get(name=name)

    def delete(self, name):
        """Pass."""
        user = self.get(name=name)
        self._delete(uuid=user["uuid"])
        return self.get()
