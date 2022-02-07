# -*- coding: utf-8 -*-
"""Test suite for assets."""
import pytest

from .test_base_assets import AssetsPrivate, AssetsPublic, ModelMixinsBase


class TestDevicesPrivate(AssetsPrivate, ModelMixinsBase):
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices


class TestDevicesPublic(AssetsPublic, ModelMixinsBase):
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices
