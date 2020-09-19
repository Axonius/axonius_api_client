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

    @pytest.mark.parametrize(
        "method, field",
        [["hostname", "FIELD_HOSTNAME"], ["mac", "FIELD_MAC"], ["ip", "FIELD_IP"]],
    )
    def test_get_bys(self, apiobj, method, field):
        """Pass."""
        self._all_get_by(apiobj=apiobj, method=method, field=field)

    def test_get_by_subnet(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_SUBNET
        row_with_val = get_rows_exist(
            apiobj=apiobj, fields=field, max_rows=1, first=False
        )
        value = get_field_vals(rows=row_with_val, field=field)[0]

        rows = apiobj.get_by_subnet(value=value, fields=field, max_rows=3)
        check_assets(rows)
        assert len(rows) >= 1

        rows_values = get_field_vals(rows=rows, field=field)
        assert value in rows_values
