# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import logging
import pathlib
import time

import pytest

from axonius_api_client.constants.logs import (
    LOG_LEVEL_CONSOLE,
    LOG_LEVEL_FILE,
    LOG_NAME_FILE,
    LOG_NAME_STDERR,
    LOG_NAME_STDOUT,
)
from axonius_api_client.exceptions import ToolsError
from axonius_api_client.logs import (
    LOG,
    add_file,
    add_null,
    add_stderr,
    add_stdout,
    del_file,
    del_null,
    del_stderr,
    del_stdout,
    get_obj_log,
    gmtime,
    localtime,
    set_log_level,
    str_level,
)


class TestLogs:
    """Test logs."""

    def test_gmtime(self):
        gmtime()
        assert logging.Formatter.converter == time.gmtime

    def test_localtime(self):
        localtime()
        assert logging.Formatter.converter == time.localtime

    def test_get_obj_log(self):
        log = get_obj_log(obj=self, level="warning")
        assert log.name == "axonius_api_client.tests.tests_pkg.test_logs.TestLogs"
        assert log.level == logging.WARNING

    def test_str_level_const(self):
        assert str_level(level=logging.DEBUG) == "DEBUG"

    def test_str_level_int(self):
        assert str_level(level=10) == "DEBUG"

    def test_str_level_int_fail(self):
        with pytest.raises(ToolsError):
            str_level(level=999)

    def test_str_level_str_int(self):
        assert str_level(level="10") == "DEBUG"

    def test_str_level_str(self):
        assert str_level(level="debug") == "DEBUG"

    def test_str_level_str_fail(self):
        with pytest.raises(ToolsError):
            str_level(level="xx")

    def test_set_log_level(self):
        obj = logging.getLogger("test")
        obj.setLevel(logging.INFO)
        set_log_level(obj=obj, level="debug")
        assert obj.level == logging.DEBUG

    def test_set_log_level_none(self):
        obj = logging.getLogger("test")
        obj.setLevel(logging.INFO)
        set_log_level(obj=obj, level=None)
        assert obj.level == logging.INFO

    def test_add_del_stderr(self):
        h = add_stderr(obj=LOG)
        assert h.name == LOG_NAME_STDERR
        assert str_level(level=h.level).lower() == LOG_LEVEL_CONSOLE
        assert isinstance(h, logging.StreamHandler)
        assert h in LOG.handlers

        dh = del_stderr(obj=LOG)
        assert isinstance(dh, dict)
        assert LOG.name in dh
        assert isinstance(dh[LOG.name], list)
        assert h in dh[LOG.name]
        assert h not in LOG.handlers

    def test_add_del_stdout(self):
        h = add_stdout(obj=LOG)
        assert h.name == LOG_NAME_STDOUT
        assert str_level(level=h.level).lower() == LOG_LEVEL_CONSOLE
        assert isinstance(h, logging.StreamHandler)
        assert h in LOG.handlers

        dh = del_stdout(obj=LOG)
        assert isinstance(dh, dict)
        assert LOG.name in dh
        assert isinstance(dh[LOG.name], list)
        assert h in dh[LOG.name]
        assert h not in LOG.handlers

    def test_add_del_null(self):
        del_null(obj=LOG)
        h = add_null(obj=LOG)
        assert h.name == "NULL"
        assert isinstance(h, logging.NullHandler)
        assert h in LOG.handlers

        fh = add_null(obj=LOG)
        assert fh is None

        dh = del_null(obj=LOG)

        assert isinstance(dh, dict)
        assert isinstance(dh[LOG.name], list)

        assert LOG.name in dh
        f = dh.pop(LOG.name)

        assert h in f
        assert h not in LOG.handlers

    def test_add_del_file(self):
        h = add_file(obj=LOG)
        assert h.name == LOG_NAME_FILE
        assert str_level(level=h.level).lower() == LOG_LEVEL_FILE
        assert isinstance(h, logging.handlers.RotatingFileHandler)
        assert h in LOG.handlers
        assert getattr(h, "PATH", None)
        assert isinstance(h.PATH, pathlib.Path)

        dh = del_file(LOG)
        assert isinstance(dh, dict)
        assert LOG.name in dh
        assert isinstance(dh[LOG.name], list)
        assert h in dh[LOG.name]
        assert h not in LOG.handlers
