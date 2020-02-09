# -*- coding: utf-8 -*-
"""API module for working with system configuration."""
from __future__ import absolute_import, division, print_function, unicode_literals

from . import mixins, routers

'''
class LifecycleSettings(mixins.Child):
    """Pass."""


class Roles(mixins.Child):
    """Pass."""


class GlobalSettings(mixins.Child):
    """Pass."""


class GuiSettings(mixins.Child):
    """Pass."""


class Users(mixins.Child):
    """Pass."""


class Settings(mixins.Model, mixins.Mixins):
    """System related API methods."""
'''


class System(mixins.Model, mixins.Mixins):
    """System related API methods."""

    def _init(self, auth, **kwargs):
        """Post init setup."""
        # children
        """
        admin.settings -> MODEL
        admin.settings.global -> CHILD
        admin.settings.lifecycle -> CHILD
        admin.settings.gui -> CHILD
        admin.roles - CHILD
        admin.user - CHILD
        """
        super(System, self)._init(auth=auth, **kwargs)

    @property
    def _router(self):
        """Router for this API client.

        Returns:
            routers.Router: The object holding the REST API routes for this object type.

        """
        return routers.ApiV1.system
