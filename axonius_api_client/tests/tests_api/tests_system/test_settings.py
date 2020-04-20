# -*- coding: utf-8 -*-
"""Test suite."""

import pytest

from axonius_api_client.exceptions import ApiError, NotFoundError

# from ...meta import TEST_PERM, TEST_ROLE

GUI_SECTION_WITH_SUBS = "system_settings"
GUI_SECTION_NO_SUBS = "ldap_login_settings"
GUI_NON_SUB_SECTION = "multiLine"
GUI_SUB_SECTION = "percentageThresholds"
GUI_SUB_KEYS = ["error", "success", "warning"]


class SettingsBase:
    """Pass."""

    def test_get(self, apiobj):
        """Pass."""
        result = apiobj.get()
        assert isinstance(result, dict)
        assert isinstance(result["section_titles"], dict) and result["section_titles"]
        assert isinstance(result["sub_sections"], dict) and result["sub_sections"]
        assert isinstance(result["sections"], dict) and result["sections"]
        assert isinstance(result["title"], str) and result["title"]
        assert isinstance(result["config"], dict) and result["config"]
        for k, v in result["sections"].items():
            assert isinstance(v, dict) and v
            assert k in result["section_titles"]
            assert k in result["sections"]


class TestSettingsGui(SettingsBase):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        """Pass."""
        return api_system.settings_gui

    def test_get_section_config_false(self, apiobj):
        """Pass."""
        result = apiobj.get_section(section=GUI_SECTION_WITH_SUBS, config=False)
        assert isinstance(result, dict)
        sub_schema = result[GUI_SUB_SECTION]["sub_schemas"]
        assert isinstance(sub_schema, dict) and sub_schema

        for k, v in result.items():
            assert isinstance(v, dict) and v
            assert isinstance(v["name"], str) and v["name"]
            assert isinstance(v.get("title", ""), str)
            assert isinstance(v["required"], bool)
            assert isinstance(v["type"], str) and v["type"]

    def test_get_section_config_true(self, apiobj):
        """Pass."""
        result = apiobj.get_section(section=GUI_SECTION_WITH_SUBS, config=True)
        assert isinstance(result, dict)
        value = result[GUI_SUB_SECTION]
        assert isinstance(value, dict) and value

    def test_get_section_error(self, apiobj):
        """Pass."""
        with pytest.raises(NotFoundError):
            apiobj.get_section(section="badwolf")

    def test_get_sub_section_error(self, apiobj):
        """Pass."""
        with pytest.raises(NotFoundError):
            apiobj.get_sub_section(section=GUI_SECTION_WITH_SUBS, sub_section="badwolf")

    def test_get_sub_section_no_subsections(self, apiobj):
        """Pass."""
        with pytest.raises(ApiError):
            apiobj.get_sub_section(section=GUI_SECTION_NO_SUBS, sub_section="badwolf")

    def test_get_sub_section_config_true(self, apiobj):
        """Pass."""
        result = apiobj.get_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, config=True
        )
        for i in GUI_SUB_KEYS:
            assert i in result

    def test_get_sub_section_config_false(self, apiobj):
        """Pass."""
        result = apiobj.get_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, config=False
        )
        assert isinstance(result, dict)
        for k, v in result.items():
            assert k in GUI_SUB_KEYS
            assert isinstance(v["name"], str) and v["name"]
            assert isinstance(v.get("title", ""), str)
            assert isinstance(v["required"], bool)
            assert isinstance(v["type"], str) and v["type"]

    def test_update_section(self, apiobj):
        """Pass."""
        old_section = apiobj.get_section(section=GUI_SECTION_WITH_SUBS, config=True)
        old_value = old_section[GUI_NON_SUB_SECTION]
        update_value = not old_value

        new_section_args = {GUI_NON_SUB_SECTION: update_value}
        new_section = apiobj.update_section(
            section=GUI_SECTION_WITH_SUBS, **new_section_args
        )
        new_value = new_section[GUI_NON_SUB_SECTION]
        assert new_value == update_value and old_value != new_value

        reset_section_args = {GUI_NON_SUB_SECTION: old_value}
        reset_section = apiobj.update_section(
            section=GUI_SECTION_WITH_SUBS, **reset_section_args
        )
        reset_value = reset_section[GUI_NON_SUB_SECTION]
        assert reset_value == old_value and reset_value != new_value

    def test_update_sub_section(self, apiobj):
        """Pass."""
        old_section = apiobj.get_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, config=True
        )
        sub_key = GUI_SUB_KEYS[0]
        old_value = old_section[sub_key]
        update_value = old_value + 1

        new_section_args = {sub_key: update_value}
        new_section = apiobj.update_sub_section(
            section=GUI_SECTION_WITH_SUBS,
            sub_section=GUI_SUB_SECTION,
            **new_section_args
        )
        new_value = new_section[sub_key]
        assert new_value == update_value and old_value != new_value

        reset_section_args = {sub_key: old_value}
        reset_section = apiobj.update_sub_section(
            section=GUI_SECTION_WITH_SUBS,
            sub_section=GUI_SUB_SECTION,
            **reset_section_args
        )
        reset_value = reset_section[sub_key]
        assert reset_value == old_value and reset_value != new_value


class TestSettingsCore(SettingsBase):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        """Pass."""
        return api_system.settings_core


class TestSettingsLifecycle(SettingsBase):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        """Pass."""
        return api_system.settings_lifecycle
