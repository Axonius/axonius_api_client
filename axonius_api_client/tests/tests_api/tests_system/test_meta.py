# -*- coding: utf-8 -*-
"""Test suite."""
import pytest


class SystemMetaBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_meta):
        return api_meta


class TestSystemMetaPrivate(SystemMetaBase):
    def val_entity_sizes(self, data):
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
        data = apiobj._about()
        assert isinstance(data, dict)
        keys = ["Build Date", "Installed Version", "Customer ID"]
        empty_ok = ["Installed Version"]

        for key in keys:
            assert key in data
            assert isinstance(data[key], str)
            if key not in empty_ok:
                assert data[key]

    def test_private_historical_sizes(self, apiobj):
        data = apiobj._historical_sizes()
        self.val_historical_sizes(data)


class TestSystemMetaPublic(SystemMetaBase):
    def test_version(self, apiobj):
        data = apiobj.version
        assert isinstance(data, str)

    def test_about(self, apiobj):
        data = apiobj.about()
        assert isinstance(data, dict)

        keys = ["Build Date", "Version", "Customer ID"]
        empty_ok = ["Version"]

        for key in keys:
            assert key in data
            assert isinstance(data[key], str)
            if key not in empty_ok:
                assert data[key]

    def test_historical_sizes(self, apiobj):
        data = apiobj.historical_sizes()
        assert isinstance(data["disk_free_mb"], float)
        assert isinstance(data["disk_used_mb"], float)
        assert isinstance(data["historical_sizes_devices"], dict)
        assert isinstance(data["historical_sizes_users"], dict)
