# -*- coding: utf-8 -*-
"""Test suite for assets."""
import pytest

from .test_base_assets import AssetsPrivate, AssetsPublic, ModelMixinsBase


class TestUsers(AssetsPrivate, AssetsPublic, ModelMixinsBase):
    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        return api_users
