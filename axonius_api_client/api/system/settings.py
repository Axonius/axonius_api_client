# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from typing import Optional

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

    TITLE: str = ""

    @property
    def router_path(self) -> str:
        """Pass."""
        raise NotImplementedError  # pragma: no cover

    def get(self) -> dict:
        """Get the current system settings.

        Returns:
            :obj:`dict`: current system settings
        """
        return parse_settings(raw=self._get(), title=self.TITLE)

    def get_section(
        self, section: str, sub_section: Optional[str] = None, full_config: bool = False
    ) -> dict:
        """Pass."""
        settings = self.get()
        title = settings["settings_title"]

        valid_sections = []

        for name, meta in settings["sections"].items():
            valid_sections.append(
                {
                    "Section Name": name,
                    "Section Title": meta["title"],
                    "Sub Section Names": "\n".join(list(meta["sub_sections"])),
                }
            )

            if name == section:
                if full_config:
                    meta["full_config"] = settings["config"]
                return meta

        err = f"Section Name {section!r} not found in {title}"
        raise NotFoundError(tablize(value=valid_sections, err=err))

    def get_sub_section(
        self, section: str, sub_section: str, full_config: bool = False
    ) -> dict:
        """Pass."""
        settings = self.get_section(section=section, full_config=full_config)
        title = settings["settings_title"]

        if not settings["sub_sections"]:
            raise ApiError(f"Section Name {section!r} has no sub sections!")

        valids = []

        for name, meta in settings["sub_sections"].items():
            valids.append(
                {
                    "Sub Section Name": meta["name"],
                    "Sub Section Title": meta["title"],
                    "Section Name": meta["parent_name"],
                    "Section Title": meta["parent_title"],
                }
            )

            if name == sub_section:
                if full_config:
                    meta["full_config"] = settings["full_config"]
                return meta

        err = (
            f"Sub Section Name {sub_section!r} not found in under "
            f"Section Name {section!r} in {title}"
        )
        raise NotFoundError(tablize(value=valids, err=err))

    def update_section(self, section: str, **kwargs) -> dict:
        """Update the system settings."""
        settings = self.get_section(section=section, full_config=True)
        title = settings["settings_title"]
        schemas = settings["schemas"]
        source = f"{title} Section Name {section!r}"
        old_config = settings["config"]
        full_config = settings["full_config"]

        new_config = {}
        new_config.update(kwargs)

        config_unknown(
            schemas=schemas, new_config=new_config, source=source,
        )
        config_build(
            schemas=schemas, old_config=old_config, new_config=new_config, source=source,
        )
        config_unchanged(
            schemas=schemas, old_config=old_config, new_config=new_config, source=source,
        )

        full_config[section] = new_config

        self._update(new_config=full_config)

        return self.get_section(section=section)

    def update_sub_section(self, section: str, sub_section: str, **kwargs) -> dict:
        """Update the system settings."""
        settings = self.get_sub_section(
            section=section, sub_section=sub_section, full_config=True
        )
        title = settings["settings_title"]
        schemas = settings["schemas"]
        source = f"{title} Section Name {section!r} Sub Section Name {sub_section!r}"
        old_config = settings["config"]
        full_config = settings["full_config"]

        new_config = {}
        new_config.update(kwargs)

        config_unknown(
            schemas=schemas, new_config=new_config, source=source,
        )
        config_build(
            schemas=schemas, old_config=old_config, new_config=new_config, source=source,
        )
        config_unchanged(
            schemas=schemas, old_config=old_config, new_config=new_config, source=source,
        )

        full_config[section][sub_section] = new_config
        self._update(new_config=full_config)

        return self.get_sub_section(section=section, sub_section=sub_section)

    def _get(self) -> dict:
        """Direct API method to get the current system settings.

        Returns:
            :obj:`dict`: current system settings
        """
        return self.request(method="get", path=self.router_path)

    def _update(self, new_config: dict) -> dict:
        """Direct API method to update the system settings."""
        return self.request(method="post", path=self.router_path, json=new_config)


class SettingsCore(SettingsChild):
    """Child API object to work with System Global Settings."""

    TITLE: str = "Global Settings"

    @property
    def router_path(self) -> str:
        """Route path for this setting object."""
        return self.parent.router.settings_core


class SettingsLifecycle(SettingsChild):
    """Child API object to work with Lifecycle Global Settings."""

    TITLE: str = "Lifecycle Settings"

    @property
    def router_path(self) -> str:
        """Route path for this setting object."""
        return self.parent.router.settings_lifecycle


class SettingsGui(SettingsChild):
    """Child API object to work with GUI Global Settings."""

    TITLE: str = "GUI Settings"

    @property
    def router_path(self) -> str:
        """Route path for this setting object."""
        return self.parent.router.settings_gui
