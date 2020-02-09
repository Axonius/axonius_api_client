# -*- coding: utf-8 -*-
"""API module for working with system configuration."""
from __future__ import absolute_import, division, print_function, unicode_literals

import warnings

from .. import exceptions, tools
from . import mixins, routers


class Settings(mixins.Model, mixins.Mixins):
    """Administrative settings."""

    def _init(self, auth, **kwargs):
        """Post init setup."""
        self.core = Core(parent=self)
        self.gui = Gui(parent=self)
        self.lifecycle = Lifecycle(parent=self)
        self.meta = Meta(parent=self)
        super(Settings, self)._init(auth=auth, **kwargs)
        warnings.warn(exceptions.BetaWarning(obj=self))

    @property
    def _router(self):
        """Router for this API client."""
        return routers.ApiV1.settings


class Meta(mixins.Child):
    """Meta information."""

    def _init(self, parent):
        """Post init setup."""
        super(Meta, self)._init(parent=parent)

    def _about(self):
        """Pass."""
        path = self._parent._router.about
        return self._parent._request(method="get", path=path)

    def _historical_sizes(self):
        """Pass."""
        path = self._parent._router.historical_sizes
        return self._parent._request(method="get", path=path)

    def about(self):
        """Pass."""
        return self._about()

    def historical_sizes(self):
        """Pass."""
        return self._historical_sizes()


class Core(mixins.Child):
    """Global settings under Administrative settings."""

    def _init(self, parent):
        """Post init setup."""
        self.aggregation = Aggregation(parent=self)
        super(Core, self)._init(parent=parent)

    def _get(self):
        """Pass."""
        path = self._parent._router.core
        return self._parent._request(method="get", path=path)

    def _update(self, config):
        path = self._parent._router.core
        return self._parent._request(method="post", path=path, json=config)

    def get(self):
        """Pass."""
        return self._get()["config"]

    def update(self, config):
        """Pass."""
        self._update(config=config)
        return self.get()


class Gui(mixins.Child):
    """GUI settings under Administrative settings."""

    def _init(self, parent):
        """Post init setup."""
        super(Gui, self)._init(parent=parent)

    def _get(self):
        """Pass."""
        path = self._parent._router.gui
        return self._parent._request(method="get", path=path)

    def _update(self, config):
        path = self._parent._router.gui
        return self._parent._request(method="post", path=path, json=config)

    def get(self):
        """Pass."""
        return self._get()["config"]

    def update(self, config):
        """Pass."""
        self._update(config=config)
        return self.get()


class Lifecycle(mixins.Child):
    """Lifecycle settings under Administrative settings."""

    def _init(self, parent):
        """Post init setup."""
        super(Lifecycle, self)._init(parent=parent)

    def _get(self):
        """Pass."""
        path = self._parent._router.lifecycle
        return self._parent._request(method="get", path=path)

    def _update(self, config):
        path = self._parent._router.lifecycle
        return self._parent._request(method="post", path=path, json=config)

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
