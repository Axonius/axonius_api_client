# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client."""
import os
import pathlib

import pytest

from axonius_api_client import PACKAGE_ROOT
from axonius_api_client.setup_env import (
    KEY_CERTWARN,
    KEY_DEFAULT_PATH,
    KEY_ENV_FILE,
    KEY_ENV_PATH,
    KEY_KEY,
    KEY_OVERRIDE,
    KEY_SECRET,
    KEY_URL,
    NO,
    YES,
    find_dotenv,
    get_env_ax,
    get_env_bool,
    get_env_connect,
    get_env_path,
    get_env_str,
)


class TestFindDotEnv:
    def test_supplied(self, monkeypatch, tmp_path):
        path = tmp_path / ".env"
        path.touch()
        src, ret = find_dotenv(ax_env=tmp_path)
        assert src == "supplied"
        assert ret == str(path)

    def test_env_path_key(self, monkeypatch, tmp_path):
        monkeypatch.setenv(KEY_ENV_PATH, str(tmp_path))
        path = tmp_path / ".env"
        path.touch()
        src, ret = find_dotenv()
        assert src == "env_path"
        assert ret == str(path)

    def test_default_env_path_key(self, monkeypatch, tmp_path):
        monkeypatch.delenv(KEY_ENV_PATH, raising=False)
        monkeypatch.delenv(KEY_DEFAULT_PATH, raising=False)
        monkeypatch.setenv(KEY_DEFAULT_PATH, str(tmp_path))
        path = tmp_path / ".env"
        path.touch()
        src, ret = find_dotenv()
        assert src == "default_path"
        assert ret == str(path)

    def test_find_dotenv_not_found(self, monkeypatch, tmp_path):
        monkeypatch.delenv(KEY_ENV_PATH, raising=False)
        monkeypatch.delenv(KEY_DEFAULT_PATH, raising=False)
        monkeypatch.setenv(KEY_ENV_FILE, "moofile")
        old_path = os.getcwd()
        os.chdir(tmp_path)
        src, ret = find_dotenv(default=None)
        os.chdir(old_path)
        assert src == "not_found"
        assert ret == ""

    def test_find_dotenv_cwd(self, monkeypatch, tmp_path):
        monkeypatch.delenv(KEY_ENV_PATH, raising=False)
        monkeypatch.delenv(KEY_DEFAULT_PATH, raising=False)
        path = tmp_path / ".env"
        path.touch()
        old_path = os.getcwd()
        os.chdir(tmp_path)
        src, ret = find_dotenv(default=None)
        os.chdir(old_path)
        assert src == "find_dotenv_cwd"
        assert ret == str(path)

    def test_find_dotenv_pkg(self, monkeypatch, tmp_path):
        monkeypatch.delenv(KEY_ENV_PATH, raising=False)
        monkeypatch.delenv(KEY_DEFAULT_PATH, raising=False)
        monkeypatch.setenv(KEY_ENV_FILE, "test.env")
        path = pathlib.Path(PACKAGE_ROOT) / "test.env"
        path.touch()
        src, ret = find_dotenv(default=None)
        path.unlink()
        assert src == "find_dotenv_pkg"
        assert ret.endswith("test.env")


class TestGetEnvStr:
    def test_default(self, monkeypatch):
        ret = get_env_str(key="boom", default="abc")
        assert ret == "abc"

    def test_lower(self, monkeypatch):
        monkeypatch.setenv("AX_TEST", " ABC ")
        ret = get_env_str(key="AX_TEST", lower=True)
        assert ret == "abc"

    def test_invalid(self, monkeypatch):
        monkeypatch.delenv("AX_TEST", raising=False)
        with pytest.raises(ValueError):
            get_env_str(key="AX_TEST")


class TestGetEnvPath:
    def test_none(self, monkeypatch):
        ret = get_env_path(key="boom")
        assert ret == ""

    def test_default(self, monkeypatch):
        ret = get_env_path(key="boom", default=os.getcwd())
        assert ret == pathlib.Path(os.getcwd()).expanduser().resolve()

    def test_default_get_dir(self, monkeypatch, tmp_path):
        path = tmp_path / "file.test"
        path.touch()
        ret = get_env_path(key="boom", default=str(path))
        assert ret == tmp_path

    def test_default_noget_dir(self, monkeypatch, tmp_path):
        path = tmp_path / "file.test"
        path.touch()
        ret = get_env_path(key="boom", default=str(path), get_dir=False)
        assert ret == path


class TestGetEnvBool:
    @pytest.mark.parametrize("value", YES, scope="class")
    def test_yes(self, value, monkeypatch):
        monkeypatch.setenv("AX_TEST", value)
        ret = get_env_bool("AX_TEST")
        assert ret is True

    @pytest.mark.parametrize("value", NO, scope="class")
    def test_no(self, value, monkeypatch):
        monkeypatch.setenv("AX_TEST", value)
        ret = get_env_bool("AX_TEST")
        assert ret is False

    def test_err(self, monkeypatch):
        monkeypatch.setenv("AX_TEST", "x")
        with pytest.raises(ValueError):
            get_env_bool("AX_TEST")

    def test_default1(self, monkeypatch):
        monkeypatch.setenv("AX_TEST", "")
        ret = get_env_bool("AX_TEST", default="yes")
        assert ret is True

    def test_default2(self, monkeypatch):
        monkeypatch.delenv("AX_TEST", raising=False)
        ret = get_env_bool("AX_TEST", default="yes")
        assert ret is True


class TestGetEnvConnect:
    def test_no_override(self, monkeypatch):
        URL = "a"
        KEY = "b"
        SEC = "c"
        WARN = "yes"
        exp = {"url": URL, "key": KEY, "secret": SEC, "certwarn": True}
        monkeypatch.setenv(KEY_URL, URL)
        monkeypatch.setenv(KEY_KEY, KEY)
        monkeypatch.setenv(KEY_SECRET, SEC)
        monkeypatch.setenv(KEY_CERTWARN, WARN)
        monkeypatch.setenv(KEY_OVERRIDE, "no")
        ret = get_env_connect()
        assert ret == exp

    def test_override(self, monkeypatch):
        URL = "a"
        KEY = "b"
        SEC = "c"
        monkeypatch.setenv(KEY_URL, URL)
        monkeypatch.setenv(KEY_KEY, KEY)
        monkeypatch.setenv(KEY_SECRET, SEC)
        monkeypatch.setenv(KEY_OVERRIDE, "yes")
        ret = get_env_connect()
        assert ret["url"]
        assert ret["key"]
        assert ret["secret"]


class TestGetEnvAx:
    def test_valid(self, monkeypatch):
        monkeypatch.setenv("AX_TEST", "boom")
        ret = get_env_ax()
        assert ret["AX_TEST"] == "boom"
