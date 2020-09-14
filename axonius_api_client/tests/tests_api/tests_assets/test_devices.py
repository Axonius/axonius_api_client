# -*- coding: utf-8 -*-
"""Test suite for assets."""
import pytest

from ...utils import check_assets, get_field_vals, get_rows_exist
from .base_assets import AssetsPrivate, AssetsPublic, ModelMixinsBase


class TestDevices(AssetsPrivate, AssetsPublic, ModelMixinsBase):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        """Pass."""
        return api_devices

    def test_get_by_hostname(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_HOSTNAME

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_hostname(value=value, field=field)
        check_assets(rows)
        assert len(rows) == 1

        rows_values = get_field_vals(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_hostname_equals_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_HOSTNAME

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_hostname(value=value, field=field, not_flag=True)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        assert value not in rows_values

    def test_get_by_hostnames(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_HOSTNAME

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_hostnames(values=values, field=field)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        for value in values:
            assert value in rows_values

    def test_get_by_hostnames_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_HOSTNAME

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_values(values=values, field=field, not_flag=True)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        for value in values:
            assert value not in rows_values

    def test_get_by_hostname_regex(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_HOSTNAME

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_hostname_regex(value=regex_value, field=field)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_hostname_regex_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_HOSTNAME

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_hostname_regex(
            value=regex_value, field=field, not_flag=True,
        )
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        assert value not in rows_values

    def test_get_by_mac(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAC

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_mac(value=value, field=field)
        check_assets(rows)
        assert len(rows) >= 1

        rows_values = get_field_vals(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_mac_equals_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAC

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_mac(value=value, field=field, not_flag=True)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        assert value not in rows_values

    def test_get_by_macs(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAC

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_macs(values=values, field=field)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        for value in values:
            assert value in rows_values

    def test_get_by_macs_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAC

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_values(values=values, field=field, not_flag=True)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        for value in values:
            assert value not in rows_values

    def test_get_by_mac_regex(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAC

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_mac_regex(value=regex_value, field=field)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_mac_regex_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAC

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_mac_regex(value=regex_value, field=field, not_flag=True)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        assert value not in rows_values

    def test_get_by_ip(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_IP

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_ip(value=value, field=field)
        check_assets(rows)
        assert len(rows) >= 1

        rows_values = get_field_vals(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_ip_equals_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_IP

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_ip(value=value, field=field, not_flag=True)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        assert value not in rows_values

    def test_get_by_ips(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_IP

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_ips(values=values, field=field)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        for value in values:
            assert value in rows_values

    def test_get_by_ips_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_IP

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_ips(values=values, field=field, not_flag=True)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        for value in values:
            assert value not in rows_values

    def test_get_by_ip_regex(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_IP

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_ip_regex(value=regex_value, field=field)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_ip_regex_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_IP

        values = get_field_vals(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_ip_regex(value=regex_value, field=field, not_flag=True)
        check_assets(rows)

        rows_values = get_field_vals(rows=rows, field=field)
        assert value not in rows_values

    def test_get_by_subnet(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_SUBNET
        rows_orig = get_rows_exist(apiobj=apiobj, fields=field)
        values = get_field_vals(rows=rows_orig, field=field)
        value = values[0]

        rows = apiobj.get_by_subnet(value=value, fields=field)
        check_assets(rows)
        assert len(rows) >= 1

        rows_values = get_field_vals(rows=rows, field=field)
        assert value in rows_values
