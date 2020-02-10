# -*- coding: utf-8 -*-
"""API module for working with system configuration."""
from __future__ import absolute_import, division, print_function, unicode_literals

import warnings

from .. import exceptions, tools
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
