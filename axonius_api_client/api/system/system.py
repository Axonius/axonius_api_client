# -*- coding: utf-8 -*-
"""API for working with system components."""
from ..mixins import ModelMixins
from ..routers import API_VERSION, Router
from .central_core import CentralCore
from .meta import Meta
from .settings import SettingsCore, SettingsGui, SettingsLifecycle
from .system_roles import SystemRoles
from .system_users import SystemUsers


class System(ModelMixins):
    """API for working with system components.

    Warning:
        This object is deprecated. Use the API objects directly:

            * :obj:`axonius_api_client.api.system.instances.Instances`
            * :obj:`axonius_api_client.api.system.settings.SettingsCore`
            * :obj:`axonius_api_client.api.system.settings.SettingsGui`
            * :obj:`axonius_api_client.api.system.settings.SettingsLifecycle`
            * :obj:`axonius_api_client.api.system.system_users.SystemUsers`
            * :obj:`axonius_api_client.api.system.system_roles.SystemRoles`
            * :obj:`axonius_api_client.api.system.meta.Meta`

    """

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.system

    def _init(self, **kwargs):
        """Mixins for API Models.

        Args:
            **kwargs: passed to each thing
        """
        self.settings_core = SettingsCore(auth=self.auth, **kwargs)
        self.settings_gui = SettingsGui(auth=self.auth, **kwargs)
        self.settings_lifecycle = SettingsLifecycle(auth=self.auth, **kwargs)
        self.users = SystemUsers(auth=self.auth, **kwargs)
        self.roles = SystemRoles(auth=self.auth, **kwargs)
        self.meta = Meta(auth=self.auth, **kwargs)
        self.central_core = CentralCore(auth=self.auth, **kwargs)
