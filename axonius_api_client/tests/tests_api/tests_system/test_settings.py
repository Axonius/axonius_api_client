# -*- coding: utf-8 -*-
"""Test suite."""

import pytest

from axonius_api_client.exceptions import ApiError, NotFoundError

GUI_SECTION_WITH_SUBS = "system_settings"
GUI_SECTION_NO_SUBS = "ldap_login_settings"
GUI_NON_SUB_SECTION = "exactSearch"
GUI_SUB_SECTION = "timeout_settings"
GUI_SUB_KEYS = ["disable_remember_me", "enabled", "timeout"]


class SettingsBasePublic:
    def val_schemas(self, schemas, config):
        for name, schema in schemas.items():
            assert schema["name"] == name
            assert schema["name"] in config
            assert isinstance(schema["required"], bool)

    def val_sub_section(self, name, meta, settings):
        assert isinstance(meta, dict) and meta
        assert meta["settings_title"] == settings["settings_title"]
        assert meta["name"] == name
        assert isinstance(meta["title"], str)
        assert isinstance(meta["schemas"], dict) and meta["schemas"]
        assert isinstance(meta["sub_sections"], dict) and not meta["sub_sections"]
        assert isinstance(meta["parent_name"], str) and meta["parent_name"]
        assert isinstance(meta["parent_title"], str) and meta["parent_title"]

        assert isinstance(meta["config"], dict)
        for k, v in meta["config"].items():
            assert not isinstance(v, dict)

        self.val_schemas(schemas=meta["schemas"], config=meta["config"])

    def val_section(self, name, meta, settings):
        assert isinstance(meta, dict) and meta
        assert meta["settings_title"] == settings["settings_title"]
        assert meta["name"] == name
        assert isinstance(meta["title"], str) and meta["title"]
        assert isinstance(meta["schemas"], dict) and meta["schemas"]
        assert isinstance(meta["sub_sections"], dict)
        assert isinstance(meta["parent_name"], str) and not meta["parent_name"]
        assert isinstance(meta["parent_title"], str) and not meta["parent_title"]

        assert isinstance(meta["config"], dict)

        self.val_schemas(schemas=meta["schemas"], config=meta["config"])
        for sub_name, sub_meta in meta["sub_sections"].items():
            self.val_sub_section(name=sub_name, meta=sub_meta, settings=settings)

    def test_get(self, apiobj):
        settings = apiobj.get()
        assert isinstance(settings, dict)

        assert isinstance(settings["settings_title"], str) and settings["settings_title"]
        assert isinstance(settings["sections"], dict) and settings["sections"]
        assert isinstance(settings["config"], dict) and settings["config"]

        for name, meta in settings["sections"].items():
            self.val_section(name=name, meta=meta, settings=settings)
            assert name in settings["config"]


class TestSettingsGui(SettingsBasePublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_settings_gui):
        return api_settings_gui

    def test_get_section_full_config_true(self, apiobj):
        result = apiobj.get_section(section=GUI_SECTION_WITH_SUBS, full_config=True)
        assert isinstance(result, dict)
        assert "full_config" in result

    def test_get_sub_section_full_config_true(self, apiobj):
        result = apiobj.get_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, full_config=True
        )
        assert isinstance(result, dict)
        assert "full_config" in result

    def test_get_section_full_config_false(self, apiobj):
        result = apiobj.get_section(section=GUI_SECTION_WITH_SUBS, full_config=False)
        assert isinstance(result, dict)
        assert "full_config" not in result

    def test_get_sub_section_full_config_false(self, apiobj):
        result = apiobj.get_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, full_config=False
        )
        assert isinstance(result, dict)
        assert "full_config" not in result

    def test_get_section_error(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_section(section="badwolf")

    def test_get_sub_section_error(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_sub_section(section=GUI_SECTION_WITH_SUBS, sub_section="badwolf")

    def test_get_sub_section_no_subsections(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.get_sub_section(section=GUI_SECTION_NO_SUBS, sub_section="badwolf")

    def test_update_section(self, apiobj):
        old_section = apiobj.get_section(section=GUI_SECTION_WITH_SUBS)
        old_config = old_section["config"]
        old_value = old_config[GUI_NON_SUB_SECTION]

        update_value = not old_value

        new_section_args = {GUI_NON_SUB_SECTION: update_value}
        new_section = apiobj.update_section(section=GUI_SECTION_WITH_SUBS, **new_section_args)
        new_value = new_section["config"][GUI_NON_SUB_SECTION]
        assert new_value == update_value and old_value != new_value

        reset_section_args = {GUI_NON_SUB_SECTION: old_value}
        reset_section = apiobj.update_section(section=GUI_SECTION_WITH_SUBS, **reset_section_args)
        reset_value = reset_section["config"][GUI_NON_SUB_SECTION]
        assert reset_value == old_value and reset_value != new_value

    def test_update_sub_section(self, apiobj):
        old_section = apiobj.get_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION
        )
        sub_key = GUI_SUB_KEYS[0]
        old_config = old_section["config"]
        old_value = old_config[sub_key]
        update_value = old_value + 1

        new_section_args = {sub_key: update_value}
        new_section = apiobj.update_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, **new_section_args
        )
        new_value = new_section["config"][sub_key]
        assert new_value == update_value and old_value != new_value

        reset_section_args = {sub_key: old_value}
        reset_section = apiobj.update_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, **reset_section_args
        )
        reset_value = reset_section["config"][sub_key]
        assert reset_value == old_value and reset_value != new_value


class TestSettingsGlobal(SettingsBasePublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_settings_global):
        return api_settings_global


class TestSettingsLifecycle(SettingsBasePublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_settings_lifecycle):
        return api_settings_lifecycle
