# -*- coding: utf-8 -*-
"""API for working with System Settings -> Lifecycle Settings."""
from .settings_mixins import SettingsMixins


class SettingsLifecycle(SettingsMixins):
    """API for working with System Settings -> Lifecycle Settings."""

    TITLE: str = "Lifecycle Settings"
    PATH: str = "settings_lifecycle"
