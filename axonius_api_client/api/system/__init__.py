# -*- coding: utf-8 -*-
"""APIs for working with system components."""
from .activity_logs import ActivityLogs
from .dashboard import Dashboard
from .instances import Instances
from .meta import Meta
from .remote_support import RemoteSupport
from .settings_global import SettingsGlobal
from .settings_gui import SettingsGui
from .settings_identity_providers import SettingsIdentityProviders
from .settings_lifecycle import SettingsLifecycle
from .signup import Signup
from .system_roles import SystemRoles
from .system_users import SystemUsers

__all__ = (
    "Dashboard",
    "Instances",
    "Meta",
    "SettingsGlobal",
    "SettingsGui",
    "SettingsLifecycle",
    "Signup",
    "SystemRoles",
    "SystemUsers",
    "RemoteSupport",
    "ActivityLogs",
    "SettingsIdentityProviders",
)
