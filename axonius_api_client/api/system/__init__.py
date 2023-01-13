# -*- coding: utf-8 -*-
"""APIs for working with system components."""
from .activity_logs import ActivityLogs
from .dashboard import Dashboard
from .dashboard_spaces import DashboardSpaces
from .data_scopes import DataScopes
from .instances import Instances
from .meta import Meta
from .remote_support import RemoteSupport
from .settings import SettingsGlobal, SettingsGui, SettingsIdentityProviders, SettingsLifecycle
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
    "DataScopes",
    "DashboardSpaces",
)
