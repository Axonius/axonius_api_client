# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import axonius_api_client as axonapi
from axonius_api_client import exceptions, tools

from .. import utils


@pytest.fixture(scope="module")
def apiobj(request):
    """Pass."""
    auth = utils.get_auth(request)

    with pytest.warns(exceptions.BetaWarning):
        api = axonapi.Settings(auth=auth)

    utils.check_apiobj_children(apiobj=api, lifecycle=axonapi.api.settings.Lifecycle)
    utils.check_apiobj_children(apiobj=api, gui=axonapi.api.settings.Gui)
    utils.check_apiobj_children(apiobj=api, core=axonapi.api.settings.Core)

    utils.check_apiobj(authobj=auth, apiobj=api)

    return api


class SettingChild(object):
    """Pass."""

    def test_get(self, apiobj):
        """Pass."""
        childobj = self.get_child_obj(apiobj)
        settings = childobj.get()
        assert isinstance(settings, dict)

    def test__get(self, apiobj):
        """Pass."""
        childobj = self.get_child_obj(apiobj)
        settings = childobj._get()
        assert isinstance(settings, dict)
        assert "config" in settings
        assert isinstance(settings["config"], dict)
        assert "schema" in settings
        assert isinstance(settings["schema"], dict)

    def test_update(self, apiobj):
        """Pass."""
        childobj = self.get_child_obj(apiobj)
        settings = childobj.get()
        updated_settings = childobj.update(config=settings)
        assert settings == updated_settings

    def test__update(self, apiobj):
        """Pass."""
        childobj = self.get_child_obj(apiobj)
        settings = childobj.get()
        ret = childobj._update(config=settings)
        assert not ret


class TestGui(SettingChild):
    """Pass."""

    def get_child_obj(self, apiobj):
        """Pass."""
        return apiobj.gui


class TestLifecycle(SettingChild):
    """Pass."""

    def get_child_obj(self, apiobj):
        """Pass."""
        return apiobj.lifecycle


class TestCore(SettingChild):
    """Pass."""

    def get_child_obj(self, apiobj):
        """Pass."""
        return apiobj.core

    def test_children(self, apiobj):
        """Pass."""
        childobj = self.get_child_obj(apiobj)
        utils.check_apiobj_children(
            apiobj=childobj, aggregation=axonapi.api.settings.Aggregation
        )


class TestAggregation(object):
    """Pass."""

    def test_get(self, apiobj):
        """Pass."""
        settings = apiobj.core.aggregation.get()
        assert isinstance(settings.pop("max_workers"), tools.INT)
        assert isinstance(settings.pop("socket_read_timeout"), tools.INT)
        assert not settings

    def test_max_workers(self, apiobj):
        """Pass."""
        settings = apiobj.core.aggregation.max_workers(value=20)
        assert settings["max_workers"] == 20

    def test_socket_read_timeout(self, apiobj):
        """Pass."""
        settings = apiobj.core.aggregation.socket_read_timeout(value=5)
        assert settings["socket_read_timeout"] == 5
