# -*- coding: utf-8 -*-
"""API for working with System Settings -> Global Settings."""
from .settings_mixins import SettingsMixins


class SettingsGlobal(SettingsMixins):
    """API for working with System Settings -> Global Settings."""

    TITLE: str = "Global Settings"
    PATH: str = "settings_global"
