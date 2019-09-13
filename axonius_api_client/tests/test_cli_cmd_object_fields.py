# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import json

import pytest

from axonius_api_client import api, cli

from . import utils


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCliObjectFields(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli, args=[cmd, "fields", "--export-format", "json"]
        )

        assert result.exit_code == 0

        json_reloaded = json.loads(result.stdout)
        assert isinstance(json_reloaded, dict)

    def test_csv(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli, args=[cmd, "fields", "--export-format", "csv"]
        )

        assert result.exit_code == 0
        utils.check_csv_cols(result.stdout, ["generic"])

    def test_get_exc_wrap(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        monkeypatch.setattr(api.users_devices.Fields, "get", utils.mock_failure)

        result = runner.invoke(cli=cli.cli, args=[cmd, "fields"])

        assert result.exit_code != 0
        stderr = result.stderr.splitlines()
        assert len(stderr) == 4
        assert (
            stderr[-2]
            == "** ERROR: WRAPPED EXCEPTION: axonius_api_client.tests.utils.MockError"
        )
        assert stderr[-1] == "badwolf"

    def test_get_exc_nowrap(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        monkeypatch.setattr(api.users_devices.Fields, "get", utils.mock_failure)

        with pytest.raises(utils.MockError):
            runner.invoke(
                cli=cli.cli,
                args=["--no-wraperror", cmd, "fields"],
                catch_exceptions=False,
            )

    def test_adapter_re(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli, args=[cmd, "fields", "--adapter-re", "generic"]
        )

        assert result.exit_code == 0

        json_reloaded = json.loads(result.stdout)
        assert isinstance(json_reloaded, dict)
        assert list(json_reloaded) == ["generic"]

    def test_adapter_fields_re(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli,
            args=[cmd, "fields", "--adapter-re", "generic", "--field-re", "name"],
        )

        assert result.exit_code == 0, result.stderr

        json_reloaded = json.loads(result.stdout)
        assert isinstance(json_reloaded, dict)
        for k, v in json_reloaded.items():
            assert k == "generic"
            for i in v:
                assert "name" in i

    def test_adapter_fields_re_err(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli,
            args=[cmd, "fields", "--adapter-re", "generic", "--field-re", "badwolf"],
        )
        assert result.exit_code != 0
        stderr = result.stderr.splitlines()
        assert stderr[-1].startswith("** ERROR: No fields found matching ")
