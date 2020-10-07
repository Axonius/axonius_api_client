# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ....constants.adapters import CSV_ADAPTER
from ....tools import json_load
from ...utils import load_clirunner


class TestGrpAdaptersFileUpload:
    def test_upload(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        args1 = [
            "adapters",
            "file-upload",
            "--name",
            CSV_ADAPTER,
            "--input-file",
            "-",
        ]
        result1 = runner.invoke(cli=cli, args=args1, input="badwolf")

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = json_load(stdout1)
        assert isinstance(json1, dict)
