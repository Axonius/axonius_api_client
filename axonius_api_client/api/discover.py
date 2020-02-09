# -*- coding: utf-8 -*-
"""API module for working with discover cycles."""
from __future__ import absolute_import, division, print_function, unicode_literals

import warnings

from .. import exceptions
from . import mixins, routers


class Discover(mixins.Model, mixins.Mixins):
    """Discover related API methods."""

    def _init(self, auth, **kwargs):
        """Post init setup."""
        super(Discover, self)._init(auth=auth, **kwargs)
        warnings.warn(exceptions.BetaWarning(obj=self))

    def _lifecycle(self):
        """Pass."""
        return self._request(method="get", path=self._router.lifecycle)

    def _start(self):
        return self._request(method="post", path=self._router.start)

    def _stop(self):
        return self._request(method="post", path=self._router.stop)

    @property
    def _router(self):
        """Router for this API client.

        Returns:
            routers.Router: The object holding the REST API routes for this object type.

        """
        return routers.ApiV1.discover

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
