# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client."""
import logging
import os
import pathlib

import pytest

from axonius_api_client import PACKAGE_ROOT
from axonius_api_client.setup_env import (
    KEY_DEFAULT_PATH,
    KEY_ENV_FILE,
    KEY_ENV_PATH,
    LOADED,
    MSG,
    Results,
    CONNECT_SCHEMAS,
    KEY_FEATURES,
    NO,
    YES,
    find_dotenv,
    get_env_ax,
    get_env_bool,
    get_env_connect,
    load_dotenv,
    get_env_csv,
    get_env_extra_warn,
    get_env_features,
    get_env_path,
    get_env_str,
    get_env_user_agent,
    set_env,
)


class TestSetEnv:
    def test_ax_env_set(self, monkeypatch, tmp_path):
        ax_env = tmp_path / ".env"
        exp = (True, "AX_TEST", "abc")
        ret = set_env(key="AX_TEST", value="abc", ax_env=ax_env)
        assert ret == exp
        contents = ax_env.read_text()
        assert contents == "AX_TEST='abc'\n"


class TestGetEnvCsv:
    def test_set(self, monkeypatch):
        monkeypatch.setenv("AX_TEST", "abc,def,ghi")
        ret = get_env_csv("AX_TEST")
        assert ret == ["abc", "def", "ghi"]


class TestGetEnvFeatures:
    def test_set(self, monkeypatch):
        monkeypatch.setenv(KEY_FEATURES, "abc,def,ghi")
        ret = get_env_features()
        assert ret == ["abc", "def", "ghi"]


class TestFindDotEnv:
    def test_supplied(self, monkeypatch, tmp_path):
        path = tmp_path / ".env"
        path.touch()
        src, ret = find_dotenv(ax_env=tmp_path)
        assert src == Results.supplied.name
        assert ret == str(path)

    def test_env_path_key(self, monkeypatch, tmp_path):
        monkeypatch.setenv(KEY_ENV_PATH, str(tmp_path))
        path = tmp_path / ".env"
        path.touch()
        src, ret = find_dotenv()
        assert src == Results.env_path.name
        assert ret == str(path)

    def test_default_env_path_key(self, monkeypatch, tmp_path):
        monkeypatch.delenv(KEY_ENV_PATH, raising=False)
        monkeypatch.delenv(KEY_DEFAULT_PATH, raising=False)
        monkeypatch.setenv(KEY_DEFAULT_PATH, str(tmp_path))
        path = tmp_path / ".env"
        path.touch()
        src, ret = find_dotenv()
        assert src == Results.default_path.name
        assert ret == str(path)

    def test_find_dotenv_not_found(self, monkeypatch, tmp_path):
        monkeypatch.delenv(KEY_ENV_PATH, raising=False)
        monkeypatch.delenv(KEY_DEFAULT_PATH, raising=False)
        monkeypatch.setenv(KEY_ENV_PATH, "badwolf")
        old_path = os.getcwd()
        os.chdir(tmp_path)
        src, ret = find_dotenv(default=None, check_walk_cwd=False, check_walk_script=False)
        os.chdir(old_path)
        assert src == Results.not_found.name
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
        assert src == Results.find_dotenv_cwd.name
        assert ret == str(path)

    def test_find_dotenv_pkg(self, monkeypatch, tmp_path):
        monkeypatch.delenv(KEY_ENV_PATH, raising=False)
        monkeypatch.delenv(KEY_DEFAULT_PATH, raising=False)
        monkeypatch.setenv(KEY_ENV_FILE, "test.env")
        path = pathlib.Path(PACKAGE_ROOT) / "test.env"
        path.touch()
        src, ret = find_dotenv(default=None)
        path.unlink()
        assert src == Results.find_dotenv_script.name
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

    def test_bytes(self, monkeypatch):
        monkeypatch.delenv("AX_TEST", raising=False)
        ret = get_env_str(key="AX_TEST", default=b"abc", lower=True)
        assert ret == "abc"


class TestGetEnvUserAgent:
    def test_default(self, monkeypatch):
        ret = get_env_user_agent()
        assert ret == ""

    def test_default_set(self, monkeypatch):
        monkeypatch.setenv("AX_USER_AGENT", "abc")
        ret = get_env_user_agent()
        assert ret == "abc"


class TestGetEnvExtraWarn:
    def test_default(self, monkeypatch):
        ret = get_env_extra_warn()
        assert ret is True

    def test_default_set(self, monkeypatch):
        monkeypatch.setenv("AX_EXTRA_WARN", "n")
        ret = get_env_extra_warn()
        assert ret is False


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

    def test_default_no_get_dir(self, monkeypatch, tmp_path):
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


def del_connect_envs(monkeypatch):
    """Clear all connect envs."""
    for k, v in CONNECT_SCHEMAS.items():
        monkeypatch.delenv(name=v["env"], raising=False)


class TestLoadDotEnv:
    def test_not_found(self, caplog, tmp_path):
        ax_env = tmp_path / ".env"
        caplog.set_level(logging.DEBUG)
        load_dotenv(
            ax_env=ax_env,
            check_ax_env=False,
            check_default=False,
            check_walk_cwd=False,
            check_walk_script=False,
        )
        assert MSG.not_found in caplog.text

    def test_found(self, caplog, monkeypatch, tmp_path):
        ax_env = tmp_path / ".env"
        ax_env.touch()
        caplog.set_level(logging.DEBUG)
        ax_env_loaded = load_dotenv(ax_env)
        assert MSG.loading in caplog.text
        assert ax_env_loaded in LOADED

        load_dotenv(ax_env, override=False)
        assert MSG.already_loaded in caplog.text


class TestGetEnvConnect:
    def test_no_override(self, monkeypatch):
        mock_envs = {
            "url": "abc",
            "key": "def",
            "secret": "ghi",
            "certwarn": "yes",
            "credentials": "n",
        }
        exp_envs = {
            "key": "def",
            "secret": "ghi",
            "certwarn": True,
            "credentials": False,
        }

        del_connect_envs(monkeypatch)

        for k, v in mock_envs.items():
            monkeypatch.setenv(CONNECT_SCHEMAS[k]["env"], v)

        ret = get_env_connect(load_override=False)
        for k, v in exp_envs.items():
            assert ret[k] == v


class TestGetEnvAx:
    def test_valid(self, monkeypatch):
        monkeypatch.setenv("AX_TEST", "boom")
        ret = get_env_ax()
        assert ret["AX_TEST"] == "boom"
