# -*- coding: utf-8 -*-
"""Parent API for working with system settings."""
from ...exceptions import ApiError, NotFoundError
from ...parsers.config import config_build, config_unchanged, config_unknown, parse_settings
from ...parsers.tables import tablize
from ..mixins import ModelMixins


class SettingsMixins(ModelMixins):
    """Parent API for working with System Settings."""

    def get(self) -> dict:
        """Get the current system settings."""
        return parse_settings(raw=self._get().to_dict(), title=self.TITLE)

    def get_section(self, section: str, full_config: bool = False) -> dict:
        """Get the current settings for a section of system settings.

        Args:
            section: name of section
            full_config: return the full configuration
        """
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

    def get_sub_section(self, section: str, sub_section: str, full_config: bool = False) -> dict:
        """Get the current settings for a sub-section of a section of system settings.

        Args:
            section: name of section
            sub_section: name of sub section of section
            full_config: return the full configuration
        """
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

    def update_section(self, section: str, check_unchanged: bool = True, **kwargs) -> dict:
        """Update the current settings for a section of system settings.

        Args:
            section: name of section
            **kwargs: settings to update
        """
        settings = self.get_section(section=section, full_config=True)
        title = settings["settings_title"]
        schemas = settings["schemas"]
        source = f"{title} Section Name {section!r}"
        old_config = settings["config"]
        full_config = settings["full_config"]

        new_config = {}
        new_config.update(kwargs)

        config_unknown(
            schemas=schemas,
            new_config=new_config,
            source=source,
        )
        config_build(
            schemas=schemas,
            old_config=old_config,
            new_config=new_config,
            source=source,
        )
        if check_unchanged:
            config_unchanged(
                schemas=schemas,
                old_config=old_config,
                new_config=new_config,
                source=source,
            )

        full_config[section] = new_config

        self._update(new_config=full_config)

        return self.get_section(section=section)

    def update_sub_section(self, section: str, sub_section: str, **kwargs) -> dict:
        """Update the current settings for a sub-section of a section of system settings.

        Args:
            section: name of section
            sub_section: name of sub section of section
            **kwargs: settings to update
        """
        settings = self.get_sub_section(section=section, sub_section=sub_section, full_config=True)
        title = settings["settings_title"]
        schemas = settings["schemas"]
        source = f"{title} Section Name {section!r} Sub Section Name {sub_section!r}"
        old_config = settings["config"]
        full_config = settings["full_config"]

        new_config = {}
        new_config.update(kwargs)

        config_unknown(
            schemas=schemas,
            new_config=new_config,
            source=source,
        )
        config_build(
            schemas=schemas,
            old_config=old_config,
            new_config=new_config,
            source=source,
        )
        config_unchanged(
            schemas=schemas,
            old_config=old_config,
            new_config=new_config,
            source=source,
        )

        full_config[section][sub_section] = new_config
        self._update(new_config=full_config)

        return self.get_sub_section(section=section, sub_section=sub_section)
