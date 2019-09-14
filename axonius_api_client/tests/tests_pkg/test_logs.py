# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import time

import pytest

import axonius_api_client as axonapi
from axonius_api_client import exceptions, logs, tools


class TestLogs(object):
    """Test logs."""

    def test_gmtime(self):
        """Pass."""
        logs.gmtime()
        assert logging.Formatter.converter == time.gmtime

    def test_localtime(self):
        """Pass."""
        logs.localtime()
        assert logging.Formatter.converter == time.localtime

    def test_get_obj_log(self):
        """Pass."""
        log = logs.get_obj_log(obj=self, level="warning")
        assert log.name == "axonius_api_client.tests.tests_pkg.test_logs.TestLogs"
        assert log.level == logging.WARNING

    def test_str_level_int(self):
        """Pass."""
        assert logs.str_level(level=10) == "DEBUG"

    def test_str_level_str_int(self):
        """Pass."""
        assert logs.str_level(level="10") == "DEBUG"

    def test_str_level_str(self):
        """Pass."""
        assert logs.str_level(level="debug") == "DEBUG"

    def test_str_level_fail(self):
        """Pass."""
        with pytest.raises(exceptions.ToolsError):
            logs.str_level(level="xx")

    def test_add_del_stderr(self):
        """Pass."""
        h = logs.add_stderr(obj=logs.LOG)
        assert h.name == axonapi.constants.LOG_NAME_STDERR
        assert (
            logs.str_level(level=h.level).lower() == axonapi.constants.LOG_LEVEL_CONSOLE
        )
        assert isinstance(h, logging.StreamHandler)
        assert h in logs.LOG.handlers

        dh = logs.del_stderr(obj=logs.LOG)
        assert isinstance(dh, dict)
        assert logs.LOG.name in dh
        assert isinstance(dh[logs.LOG.name], tools.LIST)
        assert h in dh[logs.LOG.name]
        assert h not in logs.LOG.handlers

    def test_add_del_stdout(self):
        """Pass."""
        h = logs.add_stdout(obj=logs.LOG)
        assert h.name == axonapi.constants.LOG_NAME_STDOUT
        assert (
            logs.str_level(level=h.level).lower() == axonapi.constants.LOG_LEVEL_CONSOLE
        )
        assert isinstance(h, logging.StreamHandler)
        assert h in logs.LOG.handlers

        dh = logs.del_stdout(obj=logs.LOG)
        assert isinstance(dh, dict)
        assert logs.LOG.name in dh
        assert isinstance(dh[logs.LOG.name], tools.LIST)
        assert h in dh[logs.LOG.name]
        assert h not in logs.LOG.handlers

    def test_add_del_null(self):
        """Pass."""
        logs.del_null(obj=logs.LOG)
        h = logs.add_null(obj=logs.LOG)
        assert h.name == "NULL"
        assert isinstance(h, logging.NullHandler)
        assert h in logs.LOG.handlers

        fh = logs.add_null(obj=logs.LOG)
        assert fh is None

        dh = logs.del_null(obj=logs.LOG)

        assert isinstance(dh, dict)
        assert isinstance(dh[logs.LOG.name], tools.LIST)

        assert logs.LOG.name in dh
        f = dh.pop(logs.LOG.name)

        assert h in f
        assert h not in logs.LOG.handlers
        assert not dh

    def test_add_del_file(self):
        """Pass."""
        h = logs.add_file(obj=logs.LOG)
        assert h.name == axonapi.constants.LOG_NAME_FILE
        assert logs.str_level(level=h.level).lower() == axonapi.constants.LOG_LEVEL_FILE
        assert isinstance(h, logs.logging.handlers.RotatingFileHandler)
        assert h in logs.LOG.handlers
        assert getattr(h, "PATH", None)
        assert isinstance(h.PATH, tools.pathlib.Path)

        dh = logs.del_file(logs.LOG)
        assert isinstance(dh, dict)
        assert logs.LOG.name in dh
        assert isinstance(dh[logs.LOG.name], tools.LIST)
        assert h in dh[logs.LOG.name]
        assert h not in logs.LOG.handlers
