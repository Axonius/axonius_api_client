# -*- coding: utf-8 -*-
"""Test suite."""
import copy

import pytest


class SystemMetaBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_meta):
        return api_meta

    def val_entity_sizes(self, data):
        data = copy.deepcopy(data)
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
        data = copy.deepcopy(data)
        disk_free = data.pop("disk_free")
        assert isinstance(disk_free, int) and disk_free

        disk_used = data.pop("disk_used")
        assert isinstance(disk_used, int) and disk_used

        entity_sizes = data.pop("entity_sizes")
        assert isinstance(entity_sizes, dict)

        users = entity_sizes.pop("Users", {})
        assert isinstance(users, dict) or users is None

        devices = entity_sizes.pop("Devices", {})
        assert isinstance(devices, dict) or users is None
        assert not entity_sizes
        assert not data

    def val_about(self, data):
        """Pass."""
        data = copy.deepcopy(data)
        build_date = data.pop("Build Date")
        assert isinstance(build_date, str) and build_date

        api_version = data.pop("api_client_version")
        assert isinstance(api_version, str) and api_version

        version = data.pop("Version")
        assert isinstance(version, str)

        iversion = data.pop("Installed Version")
        assert isinstance(iversion, str)

        customer_id = data.pop("Customer ID", None)
        assert isinstance(customer_id, (str, type(None)))
        assert not data


class TestSystemMetaPrivate(SystemMetaBase):
    def test_private_about(self, apiobj):
        data = apiobj._about()
        assert isinstance(data, dict)
        self.val_about(data)

    def test_private_historical_sizes(self, apiobj):
        data = apiobj._historical_sizes()
        assert isinstance(data, dict)
        self.val_historical_sizes(data)


class TestSystemMetaPublic(SystemMetaBase):
    def test_version(self, apiobj):
        data = apiobj.version
        assert isinstance(data, str)

    def test_about(self, apiobj):
        data = apiobj.about()
        assert isinstance(data, dict)
        self.val_about(data)

    def test_historical_sizes(self, apiobj):
        data = apiobj.historical_sizes()
        assert isinstance(data["disk_free_mb"], float)
        assert isinstance(data["disk_used_mb"], float)
        assert (
            isinstance(data["historical_sizes_devices"], dict)
            or data["historical_sizes_devices"] is None
        )
        assert (
            isinstance(data["historical_sizes_users"], dict)
            or data["historical_sizes_users"] is None
        )
