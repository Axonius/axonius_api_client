# -*- coding: utf-8 -*-
"""Test suite."""

from axonius_api_client.cli import cli

from ...tests_api.tests_folders.test_folders import FolderBaseEnforcements, FolderBaseQueries
from ...utils import load_clirunner


class GrpFoldersBase:
    def check_result(self, result):
        assert result.stdout
        assert result.stderr
        assert result.exit_code == 0

    def test_cmd_get_tree(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = ["folders", apiobj.TYPE, "get-tree"]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

    def test_cmd_find(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = ["folders", apiobj.TYPE, "find", "-f", "/"]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

    def test_cmd_search_crud(self, request, monkeypatch, apiobj, created_obj):
        root = apiobj.get()
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            create_name = "badwolf axonsHell create"
            create_path = root.path_public.join_under(create_name)
            copy_name = "badwolf axonsHell copy"
            copy_path = root.path_public.join_under(copy_name)
            move_name = "badwolf axonsHell move"
            move_path = root.path_public.join_under(move_name)
            self.cleanup(apiobj, [create_path, copy_path, move_path])

            args = ["folders", apiobj.TYPE, "create", "-f", create_path]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

            copied_obj = created_obj.copy(folder=create_path, refresh=True)
            created_obj.delete(confirm=True)

            args = [
                "folders",
                apiobj.TYPE,
                "search-objects",
                "-f",
                create_path,
                "-S",
                copied_obj.name,
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

            args = [
                "folders",
                apiobj.TYPE,
                "search-objects-copy",
                "--folder",
                create_path,
                "--search",
                "~.*",
                "--target",
                copy_path,
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

            args = [
                "folders",
                apiobj.TYPE,
                "search-objects-move",
                "--folder",
                copy_path,
                "--search",
                "~.*",
                "--target",
                move_path,
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

            args = [
                "folders",
                apiobj.TYPE,
                "search-objects-delete",
                "--folder",
                move_path,
                "--search",
                "~.*",
                "--confirm",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

            self.cleanup(apiobj, [create_path, copy_path, move_path])

    def test_cmd_crud(self, request, monkeypatch, apiobj):
        root = apiobj.get()
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            create_name = "badwolf axonsHell create"
            create_path = root.path_public.join_under(create_name)
            rename_name = "badwolf axonsHell rename"
            rename_path = root.path_public.join_under(rename_name)
            move_name = "badwolf axonsHell move"
            move_path = root.path_public.join_under(move_name)
            self.cleanup(apiobj, [create_path, rename_path, move_path])

            args = ["folders", apiobj.TYPE, "create", "-f", create_path]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

            args = ["folders", apiobj.TYPE, "rename", "-f", create_path, "-t", rename_name]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

            args = ["folders", apiobj.TYPE, "move", "-f", rename_path, "-t", move_path]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

            args = ["folders", apiobj.TYPE, "delete", "-f", move_path, "-c", "-ds", "-do"]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result)

            self.cleanup(apiobj, [create_path, rename_path, move_path])


class TestGrpFoldersQueries(FolderBaseQueries, GrpFoldersBase):
    pass


class TestGrpFoldersEnforcements(FolderBaseEnforcements, GrpFoldersBase):
    pass
