# -*- coding: utf-8 -*-
"""Test suite for assets."""
import pytest

from .test_base_assets import AssetsPrivate, AssetsPublic, ModelMixinsBase


class TestUsers(AssetsPrivate, AssetsPublic, ModelMixinsBase):
    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        return api_users

    @pytest.mark.parametrize(
        "method, field",
        [["username", "FIELD_USERNAME"], ["mail", "FIELD_MAIL"]],
    )
    def test_get_bys(self, apiobj, method, field):
        self._all_get_by(apiobj=apiobj, method=method, field=field)
