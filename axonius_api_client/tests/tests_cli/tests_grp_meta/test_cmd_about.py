# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import json

import pytest

from axonius_api_client import connect
from axonius_api_client.tools import json_load

from ....cli import cli
from ...utils import load_clirunner


class TestGrpMetaCmdAbout:
    ARGS = ["system", "meta", "about"]

    def test_export_json(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            result = runner.invoke(cli=cli, args=[*self.ARGS, "--export-format", "json"])
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

    def test_export_str(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            result = runner.invoke(cli=cli, args=[*self.ARGS, "--export-format", "str"])
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0


@pytest.mark.parametrize("option", ["header", "cookie"])
class TestDictOptions:
    ARGS = ["system", "meta", "about"]

    def test_cmdline(self, request, monkeypatch, option):
        orig = {"k1": "v1", "foobar": "cmdline"}
        cmdline = []
        for k, v in orig.items():
            cmdline += [f"--{option}", f"{k}={v}"]

        def checker(self):
            """Pass."""
            session = self.HTTP.session
            obj = getattr(session, f"{option}s")
            for k, v in orig.items():
                assert obj[k] == v

        runner = load_clirunner(request, monkeypatch)
        with monkeypatch.context() as m:
            m.setattr(connect.Connect, "_init", checker)
            with runner.isolated_filesystem():
                result = runner.invoke(cli=cli, args=[*cmdline, *self.ARGS])
                assert result.stdout
                assert result.stderr
                assert result.exit_code == 0

    def test_env_csv(self, request, monkeypatch, option):
        orig = {"k1": "v1", "foobar": "csv"}
        env_value = ",".join([f"{k}={v}" for k, v in orig.items()])

        def checker(self):
            """Pass."""
            session = self.HTTP.session
            obj = getattr(session, f"{option}s")
            for k, v in orig.items():
                assert obj[k] == v

        runner = load_clirunner(request, monkeypatch)
        with monkeypatch.context() as m:
            m.setattr(connect.Connect, "_init", checker)
            m.setenv(f"AX_{option.upper()}S", env_value)
            with runner.isolated_filesystem():
                result = runner.invoke(cli=cli, args=[*self.ARGS])
                assert result.stdout
                assert result.stderr
                assert result.exit_code == 0

    def test_env_csv_semi(self, request, monkeypatch, option):
        orig = {"k1": "v1", "foobar": "csv"}
        env_value = "semi:" + ";".join([f"{k}={v}" for k, v in orig.items()])

        def checker(self):
            """Pass."""
            session = self.HTTP.session
            obj = getattr(session, f"{option}s")
            for k, v in orig.items():
                assert obj[k] == v

        runner = load_clirunner(request, monkeypatch)
        with monkeypatch.context() as m:
            m.setattr(connect.Connect, "_init", checker)
            m.setenv(f"AX_{option.upper()}S", env_value)
            with runner.isolated_filesystem():
                result = runner.invoke(cli=cli, args=[*self.ARGS])
                assert result.stdout
                assert result.stderr
                assert result.exit_code == 0

    def test_env_json(self, request, monkeypatch, option):
        orig = {"k1": "v1", "foobar": "json"}
        env_value = f"json:{json.dumps(orig)}"

        def checker(self):
            """Pass."""
            session = self.HTTP.session
            obj = getattr(session, f"{option}s")
            for k, v in orig.items():
                assert obj[k] == v

        runner = load_clirunner(request, monkeypatch)
        with monkeypatch.context() as m:
            m.setattr(connect.Connect, "_init", checker)
            m.setenv(f"AX_{option.upper()}S", env_value)
            with runner.isolated_filesystem():
                result = runner.invoke(cli=cli, args=[*self.ARGS])
                assert result.stdout
                assert result.stderr
                assert result.exit_code == 0
