# -*- coding: utf-8 -*-
"""Test suite."""
import pytest


class SystemDiscoverBase:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        """Pass."""
        return api_system.discover


class TestSystemDiscoverPrivate(SystemDiscoverBase):
    """Pass."""

    def test_private_lifecycle(self, apiobj):
        """Pass."""
        lifecycle = apiobj._get()
        assert isinstance(lifecycle, dict)
        assert "status" in lifecycle
        assert lifecycle["status"] in ["starting", "running", "done"]

    def test_private_start_stop(self, apiobj):
        """Pass."""
        stop = apiobj._stop()
        assert not stop

        lifecycle = apiobj._get()
        assert lifecycle["status"] in ["done", "stopping"]

        start = apiobj._start()
        assert not start

        lifecycle = apiobj._get()
        assert lifecycle["status"] in ["starting", "running"]

        re_stop = apiobj._stop()
        assert not re_stop

        lifecycle = apiobj._get()
        assert lifecycle["status"] in ["done", "stopping"]


class TestSystemDiscoverPublic(SystemDiscoverBase):
    """Pass."""

    def test_get(self, apiobj):
        """Pass."""
        lifecycle = apiobj.get()
        assert isinstance(lifecycle, dict)
        assert isinstance(lifecycle["is_running"], bool)

    def test_start_stop(self, apiobj):
        """Pass."""
        if apiobj.is_running:
            stopped = apiobj.stop()
            assert isinstance(stopped, dict)
            assert not stopped["is_running"]
            # assert not stopped["status"] == "done"

        started = apiobj.start()
        assert isinstance(started, dict)
        assert started["is_running"]
        # assert started["status"] in ["starting", "running"]

        re_stopped = apiobj.stop()
        assert isinstance(re_stopped, dict)
        assert not re_stopped["is_running"]
        # assert re_stopped["status"] == "done"
