# -*- coding: utf-8 -*-
"""Test suite."""
import pytest


class TestSystemDiscover:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        """Pass."""
        return api_system.discover

    def test_lifecycle(self, apiobj):
        """Pass."""
        lifecycle = apiobj.lifecycle()
        assert isinstance(lifecycle, dict)
        assert "status" in lifecycle
        assert lifecycle["status"] in ["starting", "running", "done"]

    def test__lifecycle(self, apiobj):
        """Pass."""
        lifecycle = apiobj._lifecycle()
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
        assert started["status"] in ["starting", "running"]

        re_stopped = apiobj.stop()
        assert isinstance(re_stopped, dict)
        assert re_stopped["status"] == "done"
