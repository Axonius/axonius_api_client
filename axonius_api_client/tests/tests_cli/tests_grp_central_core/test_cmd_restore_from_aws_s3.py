# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli

from ...utils import load_clirunner


class TestGrpCentralCoreCmdRestoreFromAwsS3:
    def test_fail(self, request, monkeypatch):
        # no way to easily automate this, so this will fail in our current suite

        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "central-core",
                "restore-from-aws-s3",
                "--key-name",
                "badwolf",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code == 1
