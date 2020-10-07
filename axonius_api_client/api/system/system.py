# -*- coding: utf-8 -*-
"""API for working with system components ``[DEPRECATED]``."""
from ..mixins import ModelMixins
from ..routers import API_VERSION, Router
from .central_core import CentralCore
from .meta import Meta
from .settings_global import SettingsGlobal
from .settings_gui import SettingsGui
from .settings_lifecycle import SettingsLifecycle
from .system_roles import SystemRoles
from .system_users import SystemUsers


class System(ModelMixins):  # pragma: no cover
    """API for working with system components ``[DEPRECATED]``.

    Warning:
        This object is deprecated.
    """

    @property
    def router(self) -> Router:  # pragma: no cover
        """Router for this API model ``[DEPRECATED]``."""
        return API_VERSION.system

    def _init(self, **kwargs):  # pragma: no cover
        """Do not use ``[DEPRECATED]``."""
        self.settings_global = SettingsGlobal(auth=self.auth, **kwargs)
        self.settings_gui = SettingsGui(auth=self.auth, **kwargs)
        self.settings_lifecycle = SettingsLifecycle(auth=self.auth, **kwargs)
        self.users = SystemUsers(auth=self.auth, **kwargs)
        self.roles = SystemRoles(auth=self.auth, **kwargs)
        self.meta = Meta(auth=self.auth, **kwargs)
        self.central_core = CentralCore(auth=self.auth, **kwargs)
