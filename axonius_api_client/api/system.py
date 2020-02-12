# -*- coding: utf-8 -*-
"""API module for working with system configuration."""
from __future__ import absolute_import, division, print_function, unicode_literals

import warnings

from .. import exceptions, tools, constants
from . import mixins, routers


class System(mixins.Model, mixins.Mixins):
    """System methods."""

    @property
    def _router(self):
        """Router for this API client."""
        return routers.ApiV1.system

    @property
    def instances(self):
        """Pass."""
        if not hasattr(self, "_instances"):
            self._instances = Instances(parent=self)
        return self._instances

    @property
    def settings(self):
        """Pass."""
        if not hasattr(self, "_settings"):
            self._settings = Settings(parent=self)
        return self._settings

    @property
    def meta(self):
        """Pass."""
        if not hasattr(self, "_meta"):
            self._meta = Meta(parent=self)
        return self._meta

    @property
    def discover(self):
        """Pass."""
        if not hasattr(self, "_discover"):
            self._discover = Discover(parent=self)
        return self._discover

    @property
    def users(self):
        """Pass."""
        if not hasattr(self, "_users"):
            self._users = Users(parent=self)
        return self._users

    @property
    def roles(self):
        """Pass."""
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
    """Discover related API methods."""

    def _lifecycle(self):
        """Pass."""
        path = self._router.discover_lifecycle
        return self._request(method="get", path=path)

    def _start(self):
        path = self._router.discover_start
        return self._request(method="post", path=path)

    def _stop(self):
        path = self._router.discover_stop
        return self._request(method="post", path=path)

    def lifecycle(self):
        """Pass."""
        return self._lifecycle()

    @property
    def is_running(self):
        """Pass."""
        return not self.lifecycle()["status"] == "done"

    def start(self):
        """Pass."""
        if not self.is_running:
            self._start()
        return self.lifecycle()

    def stop(self):
        """Pass."""
        if self.is_running:
            self._stop()
        return self.lifecycle()


class Instances(mixins.Child):
    """Instance methods."""

    def _init(self, parent):
        """Post init setup."""
        super(Instances, self)._init(parent=parent)
        warnings.warn(exceptions.BetaWarning(obj=self))

    def _get(self):
        """Pass.

        {
            "connection_data": {
                "host": "<axonius-hostname>",
                "key": "QV2bu53oV3HMGugMOvgNSa1B5dNCDCY0"
            },
            "instances": [
                {
                    "hostname": "builds-vm-jim-2-15-b-1581114965-000",
                    "ips": [
                        "10.20.0.100"
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
        """Pass.

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
        """Pass."""
        return self._get()


class Meta(mixins.Child):
    """Meta information."""

    def _init(self, parent):
        """Post init setup."""
        super(Meta, self)._init(parent=parent)

    def _about(self):
        """Pass."""
        path = self._router.meta_about
        return self._request(method="get", path=path)

    def _historical_sizes(self):
        """Pass."""
        path = self._router.meta_historical_sizes
        return self._request(method="get", path=path)

    def about(self):
        """Pass."""
        return self._about()

    def historical_sizes(self):
        """Pass."""
        return self._historical_sizes()


class Settings(mixins.Child):
    """Administrative settings."""

    def _init(self, parent):
        """Post init setup."""
        super(Settings, self)._init(parent=parent)
        warnings.warn(exceptions.BetaWarning(obj=self))

    @property
    def core(self):
        """Pass."""
        if not hasattr(self, "_settings_core"):
            self._settings_core = SettingsCore(parent=self)
        return self._settings_core

    @property
    def gui(self):
        """Pass."""
        if not hasattr(self, "_settings_gui"):
            self._settings_gui = SettingsGui(parent=self)
        return self._settings_gui

    @property
    def lifecycle(self):
        """Pass."""
        if not hasattr(self, "_settings_lifecycle"):
            self._settings_lifecycle = SettingsLifecycle(parent=self)
        return self._settings_lifecycle


class SettingsCore(mixins.Child):
    """Global settings under Administrative settings."""

    @property
    def aggregation(self):
        """Pass."""
        if not hasattr(self, "_aggregation"):
            self._aggregation = Aggregation(parent=self)
        return self._aggregation

    def _get(self):
        """Pass."""
        path = self._router.settings_core
        return self._request(method="get", path=path)

    def _update(self, config):
        path = self._router.settings_core
        return self._request(method="post", path=path, json=config)

    def get(self):
        """Pass."""
        return self._get()["config"]

    def update(self, config):
        """Pass."""
        self._update(config=config)
        return self.get()


class SettingsGui(mixins.Child):
    """GUI settings under Administrative settings."""

    def _get(self):
        """Pass."""
        path = self._router.settings_gui
        return self._request(method="get", path=path)

    def _update(self, config):
        path = self._router.settings_gui
        return self._request(method="post", path=path, json=config)

    def get(self):
        """Pass."""
        return self._get()["config"]

    def update(self, config):
        """Pass."""
        self._update(config=config)
        return self.get()


class SettingsLifecycle(mixins.Child):
    """Lifecycle settings under Administrative settings."""

    def _get(self):
        """Pass."""
        path = self._router.settings_lifecycle
        return self._request(method="get", path=path)

    def _update(self, config):
        path = self._router.settings_lifecycle
        return self._request(method="post", path=path, json=config)

    def get(self):
        """Pass."""
        return self._get()["config"]

    def update(self, config):
        """Pass."""
        self._update(config=config)
        return self.get()


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
        tools.val_type(value=value, types=tools.INT)
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
        tools.val_type(value=value, types=tools.INT)
        settings = self._parent.get()
        settings[self._subkey]["socket_read_timeout"] = value
        self._parent.update(config=settings)
        return self.get()


class Roles(mixins.Child):
    """Role controls."""

    def _get_default(self):
        """Pass."""
        path = self._router.roles_default
        return self._request(method="get", path=path, error_json_invalid=False)

    def _set_default(self, name):
        """Pass."""
        data = {"name": name}
        path = self._router.roles_default
        return self._request(method="post", path=path, json=data)

    def _get(self):
        """Pass."""
        path = self._router.roles
        return self._request(method="get", path=path)

    def _add(self, name, permissions):
        """Pass."""
        data = {"name": name, "permissions": permissions}
        path = self._router.roles
        return self._request(method="put", path=path, json=data)

    def _update(self, name, permissions):
        """Pass."""
        data = {"name": name, "permissions": permissions}
        path = self._router.roles
        return self._request(
            method="post", path=path, json=data, error_json_invalid=False
        )

    def _delete(self, name):
        """Pass."""
        data = {"name": name}
        path = self._router.roles
        return self._request(
            method="delete", path=path, json=data, error_json_invalid=False
        )

    def set_default(self, name):
        """Pass."""
        role = self.get(name=name)
        self._set_default(name=name)
        return role

    def get_default(self):
        """Pass."""
        name = self._get_default()
        return self.get(name=name)

    def get(self, name=None):
        """Pass."""
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
