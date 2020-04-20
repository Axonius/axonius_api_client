# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
import copy

from ...exceptions import ApiError, NotFoundError
from ..mixins import ChildMixins
from ..parsers.config import (
    config_build,
    config_unchanged,
    config_unknown,
    parse_settings,
)
from ..parsers.tables import tablize


class SettingsChild(ChildMixins):
    """Child API object to work with system settings."""

    PRETTY_NAME = ""

    @property
    def router_path(self):
        """Pass."""
        raise NotImplementedError  # pragma: no cover

    def get(self):
        """Get the current system settings.

        Returns:
            :obj:`dict`: current system settings
        """
        return parse_settings(raw=self._get(), pretty_name=self.PRETTY_NAME)

    def get_section(self, section, settings=None, config=False):
        """Pass."""
        settings = settings or self.get()

        valid = []

        for name, schemas in settings["sections"].items():
            if section == name:
                if config:
                    return settings["config"][name]
                return schemas

            title = settings["section_titles"][name]
            valid.append({"name": name, "title": title})

        title = settings["title"]
        err = f"Section {section!r} not found in {title!r}"
        raise NotFoundError(tablize(value=valid, err=err))

    def get_sub_section(self, section, sub_section, settings=None, config=False):
        """Pass."""
        settings = settings or self.get()
        settings_section = self.get_section(section=section, settings=settings)

        valid = []
        for name, schemas in settings_section.items():
            if schemas.get("sub_schemas"):
                if sub_section == name:
                    if config:
                        return settings["config"][section][sub_section]
                    return schemas["sub_schemas"]

                title = schemas["title"]
                valid.append({"name": name, "title": title})

        title = settings["title"]
        if not valid:
            raise ApiError(f"Section {section!r} in {title} has no sub sections!")

        err = f"Sub section {sub_section!r} not found in section {section!r} in {title}"
        raise NotFoundError(tablize(value=valid, err=err))

    def update_section(self, section, **kwargs):
        """Update the system settings."""
        settings = self.get()
        settings_config_orig = settings["config"]
        settings_config = copy.deepcopy(settings_config_orig)

        schemas = self.get_section(section=section, settings=settings)
        section_config = settings_config[section]
        new_config = {}
        new_config.update(kwargs)

        source = f"settings section {section!r}"
        config_unknown(
            schemas=schemas, new_config=new_config, source=source,
        )
        config_build(
            schemas=schemas,
            old_config=section_config,
            new_config=new_config,
            source=source,
            check=True,
            callbacks=None,
        )
        settings_config[section].update(new_config)
        config_unchanged(
            schemas=schemas,
            old_config=settings_config_orig,
            new_config=settings_config,
            source=source,
        )
        self._update(new_config=settings_config)
        return self.get_section(section=section, config=True)

    def update_sub_section(self, section, sub_section, **kwargs):
        """Update the system settings."""
        settings = self.get()
        settings_config_orig = settings["config"]
        settings_config = copy.deepcopy(settings_config_orig)

        schemas = self.get_sub_section(
            section=section, sub_section=sub_section, settings=settings
        )
        section_config = settings_config[section][sub_section]

        new_config = {}
        new_config.update(kwargs)

        source = f"settings section {section!r} sub section {sub_section!r}"
        config_unknown(
            schemas=schemas, new_config=new_config, source=source,
        )
        config_build(
            schemas=schemas,
            old_config=section_config,
            new_config=new_config,
            source=source,
            check=True,
            callbacks=None,
        )
        settings_config[section][sub_section].update(new_config)
        config_unchanged(
            schemas=schemas,
            old_config=settings_config_orig,
            new_config=settings_config,
            source=source,
        )
        self._update(new_config=settings_config)
        return self.get_sub_section(
            section=section, sub_section=sub_section, config=True
        )

    def _get(self):
        """Direct API method to get the current system settings.

        Returns:
            :obj:`dict`: current system settings
        """
        return self.request(method="get", path=self.router_path)

    def _update(self, new_config):
        """Direct API method to update the system settings."""
        return self.request(method="post", path=self.router_path, json=new_config)


class SettingsCore(SettingsChild):
    """Child API object to work with System Global Settings."""

    PRETTY_NAME = "Global Settings"

    @property
    def router_path(self):
        """Route path for this setting object."""
        return self.parent.router.settings_core


class SettingsLifecycle(SettingsChild):
    """Child API object to work with Lifecycle Global Settings."""

    PRETTY_NAME = "Lifecycle Settings"

    @property
    def router_path(self):
        """Route path for this setting object."""
        return self.parent.router.settings_lifecycle


class SettingsGui(SettingsChild):
    """Child API object to work with GUI Global Settings."""

    PRETTY_NAME = "GUI Settings"

    @property
    def router_path(self):
        """Route path for this setting object."""
        return self.parent.router.settings_gui
