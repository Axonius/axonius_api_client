# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import axonius_api_client as axonapi
from axonius_api_client import exceptions

from .. import utils


@pytest.fixture(scope="module")
def apiobj(request):
    """Pass."""
    auth = utils.get_auth(request)

    with pytest.warns(exceptions.BetaWarning):
        api = axonapi.Discover(auth=auth)

    utils.check_apiobj(authobj=auth, apiobj=api)

    return api


class TestDiscover(object):
    """Pass."""

    def test_get_lifecycle(self, apiobj):
        """Pass."""
        lifecycle = apiobj.lifecycle()
        assert isinstance(lifecycle, dict)
        assert "status" in lifecycle
        assert lifecycle["status"] in ["starting", "running", "done"]

    def test_get__lifecycle(self, apiobj):
        """Pass."""
        lifecycle = apiobj.lifecycle()
        assert isinstance(lifecycle, dict)
        assert "status" in lifecycle
        assert lifecycle["status"] in ["starting", "running", "done"]

    def test_start_stop_lifecycle(self, apiobj):
        """Pass."""
        if apiobj.is_running:
            stopped = apiobj.stop()
            assert isinstance(stopped, dict)
            assert stopped["status"] == "done"

        started = apiobj.start()
        assert isinstance(started, dict)
        assert started["status"] in ["starting", "done"]

        re_stopped = apiobj.stop()
        assert isinstance(re_stopped, dict)
        assert re_stopped["status"] == "done"
