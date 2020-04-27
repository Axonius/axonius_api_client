# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from ..mixins import ModelMixins
from ..routers import API_VERSION
from .central_core import CentralCore
from .discover import Discover
from .meta import Meta
from .nodes import Nodes
from .roles import Roles
from .settings import SettingsCore, SettingsGui, SettingsLifecycle
from .users import Users


class System(ModelMixins):
    """System methods."""

    @property
    def router(self):
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        return API_VERSION.system

    def _init(self, auth, **kwargs):
        """Post init method for subclasses to use for extra setup.

        Args:
            auth (:obj:`.auth.Model`): object to use for auth and sending API requests
        """
        self.nodes = Nodes(parent=self)
        self.settings_core = SettingsCore(parent=self)
        self.settings_gui = SettingsGui(parent=self)
        self.settings_lifecycle = SettingsLifecycle(parent=self)
        self.meta = Meta(parent=self)
        self.discover = Discover(parent=self)
        self.users = Users(parent=self)
        self.roles = Roles(parent=self)
        self.central_core = CentralCore(parent=self)
        super(System, self)._init(auth=auth, **kwargs)
