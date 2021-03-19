# -*- coding: utf-8 -*-
"""Test suite for assets."""
import pytest

from .test_base_assets import AssetsPrivate, AssetsPublic, ModelMixinsBase


class TestDevices(AssetsPrivate, AssetsPublic, ModelMixinsBase):
    @pytest.fixture(scope="class")
    def apiobj(self, api_client):
        return api_client.devices
