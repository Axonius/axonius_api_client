# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from ...meta import ABOUT_KEYS, ABOUT_KEYS_EMPTY_OK


class SystemMetaBase:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        """Pass."""
        return api_system.meta

    def val_about(self, data):
        """Pass."""
        assert isinstance(data, dict)

        keys = ABOUT_KEYS
        empty_ok = ABOUT_KEYS_EMPTY_OK

        for key in keys:
            assert key in data
            assert isinstance(data[key], str)
            if key not in empty_ok:
                assert data[key]


class TestSystemMetaPrivate(SystemMetaBase):
    """Pass."""

    def val_entity_sizes(self, data):
        """Pass."""
        avg_document_size = data("avg_document_size")
        assert isinstance(avg_document_size, int)
        capped = data("capped")
        assert isinstance(capped, int)
        entities_last_point = data("entities_last_point")
        assert isinstance(entities_last_point, int)
        size = data("size")
        assert isinstance(size, int)
        assert not data

    def val_historical_sizes(self, data):
        """Pass."""
        disk_free = data.pop("disk_free")
        assert isinstance(disk_free, int) and disk_free

        disk_used = data.pop("disk_used")
        assert isinstance(disk_used, int) and disk_used

        entity_sizes = data.pop("entity_sizes")
        assert isinstance(entity_sizes, dict)

        users = entity_sizes.pop("Users", {})
        assert isinstance(users, dict)

        devices = entity_sizes.pop("Devices", {})
        assert isinstance(devices, dict)
        assert not entity_sizes
        assert not data

    def test_private_about(self, apiobj):
        """Pass."""
        data = apiobj._about()
        self.val_about(data)

    def test_private_historical_sizes(self, apiobj):
        """Pass."""
        data = apiobj._historical_sizes()
        self.val_historical_sizes(data)


class TestSystemMetaPublic(SystemMetaBase):
    """Pass."""

    def test_about(self, apiobj):
        """Pass."""
        data = apiobj.about()
        self.val_about(data)

    def test_historical_sizes(self, apiobj):
        """Pass."""
        data = apiobj.historical_sizes()
        assert isinstance(data["disk_free_mb"], int)
        assert isinstance(data["disk_used_mb"], int)
        assert isinstance(data["historical_sizes_devices"], dict)
        assert isinstance(data["historical_sizes_users"], dict)
