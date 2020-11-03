# -*- coding: utf-8 -*-
"""API for working with System Settings -> GUI Settings."""
from .settings_mixins import SettingsMixins


class SettingsGui(SettingsMixins):
    """API for working with System Settings -> GUI Settings."""

    TITLE: str = "GUI Settings"
    PATH: str = "settings_gui"
