# -*- coding: utf-8 -*-
"""Test suite."""
import os
import pathlib
import tempfile
import pytest
import subprocess

# noinspection PyProtectedMember
from axonius_api_client.projects.cf_token.tools import (
    is_url,
    listify,
    get_cmd_stderr,
    get_cmd_stdout,
    get_cmd_command,
    get_cmd_exit_code,
    get_cmd_timeout,
    get_cmd_strs,
    echoer,
    join_it,
    bytes_to_str,
    strip_it,
    args_str,
    coerce_str,
    coerce_path,
    is_executable,
    is_file,
    is_token,
    check_is_file,
    check_is_file_executable,
    which,
    find_cloudflared,
    check_is_token,
    get_env_path_raw,
    get_env_path,
    get_env_path_str,
    get_env_token,
    get_env_url,
    check_result_is_token,
    run_command,
    patch_subprocess,
    _called_str_original,
    _called_str_patched,
    _timeout_str_original,
    _timeout_str_patched,
)

from axonius_api_client.projects.cf_token import constants
from .meta import (
    get_token_bad,
    get_token_good,
    MOCK_OS_PATH,
    MOCK_OS_PATHS,
    MOCK_RUN,
    MOCK_ERROR,
    MOCK_TIMEOUT,
    get_url_good,
    get_url_bad,
    patch_clear_url_envs,
    patch_clear_token_envs,
)


def generator():
    """Test."""
    for x in range(2):
        yield x


class TestRunCommand:
    def test_run_command(self):
        """Test that running a command that works on windows and linux works."""
        result = run_command(command=["echo", "hello"], error=True)
        assert result.stdout == "hello\n"
        assert result.stderr == ""
        assert result.returncode == 0

    def test_run_error(self):
        """Test that running a command that DOES NOT work on windows and linux has an error."""
        with pytest.raises(subprocess.CalledProcessError) as exc:
            run_command(command=["type", "1/21"], error=True)

        assert "STDOUT" in str(exc.value)
        assert "STDERR" in str(exc.value)

    def test_run_error_no_output(self):
        with pytest.raises(subprocess.CalledProcessError) as exc:
            run_command(command=["type", "1/21"], error=True, include_output=False)

        assert "STDOUT" not in str(exc.value)
        assert "STDERR" not in str(exc.value)

    def test_run_error_timeout(self):
        with pytest.raises(subprocess.TimeoutExpired) as exc:
            run_command(command=["ping", "www.google.com"], error=True, timeout=1)

        assert "STDOUT" in str(exc.value)
        assert "STDERR" in str(exc.value)


class TestResultIsToken:
    def test_found_good(self):
        token = get_token_good()
        run = subprocess.CompletedProcess(
            args=["foo"], returncode=0, stdout=f"\n\n{token}", stderr=""
        )
        data = check_result_is_token(result=run)
        assert data == token

    def test_found_bad_unexpected(self):
        token = get_token_bad()
        run = subprocess.CompletedProcess(
            args=["foo"], returncode=0, stdout=f"\n\n{token}", stderr=""
        )
        with pytest.raises(ValueError):
            check_result_is_token(result=run)

    def test_not_found_error(self):
        error = subprocess.CalledProcessError(
            returncode=1, cmd="foo", output="stdout", stderr="do login to get token"
        )
        with pytest.raises(ValueError):
            check_result_is_token(result=error)

    def test_not_found_timeout_error(self):
        error = subprocess.TimeoutExpired(
            timeout=1, cmd="foo", output="stdout", stderr="do login to get token"
        )
        with pytest.raises(ValueError):
            check_result_is_token(result=error)

    def test_not_found_error_empty(self):
        error = subprocess.CalledProcessError(returncode=1, cmd="foo", output="stdout", stderr="")
        with pytest.raises(ValueError):
            check_result_is_token(result=error)


class TestGetEnvUrl:
    def test_found_good(self, monkeypatch):
        for key in constants.URL_ENVS:
            patch_clear_url_envs(monkeypatch)

            url = get_url_good()
            monkeypatch.setenv(key, url)
            assert get_env_url() == url

    def test_found_bad(self, monkeypatch):
        for key in constants.URL_ENVS:
            patch_clear_url_envs(monkeypatch)
            url = get_url_bad()
            monkeypatch.setenv(key, url)
            with pytest.raises(ValueError):
                get_env_url(error=True)

    def test_not_found_no_error_empty(self, monkeypatch):
        patch_clear_url_envs(monkeypatch)
        assert get_env_url(error_empty=False) is None

    def test_not_found_error_empty(self, monkeypatch):
        patch_clear_url_envs(monkeypatch)
        with pytest.raises(ValueError):
            get_env_url(error_empty=True)


class TestGetEnvToken:
    # need to test multiple keys where first is not supplied but second is
    def test_found_good(self, monkeypatch):
        for key in constants.TOKEN_ENVS:
            patch_clear_token_envs(monkeypatch)
            token = get_token_good()
            monkeypatch.setenv(key, token)
            assert get_env_token() == token

    def test_not_found_no_error_empty(self, monkeypatch):
        patch_clear_token_envs(monkeypatch)
        assert get_env_token() is None

    def test_found_bad(self, monkeypatch):
        for key in constants.TOKEN_ENVS:
            patch_clear_token_envs(monkeypatch)
            token = get_token_bad()
            monkeypatch.setenv(key, token)
            with pytest.raises(ValueError):
                get_env_token(error=True)

    def test_not_found_error_empty(self, monkeypatch):
        patch_clear_token_envs(monkeypatch)
        with pytest.raises(ValueError):
            get_env_token(error_empty=True)


class TestGetCmds:
    @pytest.mark.parametrize(
        "value, exp", [[MOCK_RUN, "stderr"], [MOCK_ERROR, "stderr"], [None, ""]]
    )
    def test_get_cmd_stderr(self, value, exp):
        data = get_cmd_stderr(value)
        assert data == exp

    @pytest.mark.parametrize(
        "value, exp", [[MOCK_RUN, "stdout"], [MOCK_ERROR, "stdout"], [None, ""]]
    )
    def test_get_cmd_stdout(self, value, exp):
        data = get_cmd_stdout(value)
        assert data == exp

    @pytest.mark.parametrize("value, exp", [[MOCK_RUN, "foo"], [MOCK_ERROR, "foo"], [None, ""]])
    def test_get_cmd_command(self, value, exp):
        data = get_cmd_command(value)
        assert data == exp

    @pytest.mark.parametrize("value", [[MOCK_RUN], [MOCK_ERROR], [None]])
    def test_get_cmd_exit_code(self, value):
        exp = getattr(value, "returncode", None)
        data = get_cmd_exit_code(value)
        assert data == exp

    @pytest.mark.parametrize("value", [[MOCK_RUN], [MOCK_ERROR], [MOCK_TIMEOUT], [None]])
    def test_get_cmd_timeout(self, value):
        exp = getattr(value, "timeout", None)
        data = get_cmd_timeout(value)
        assert data == exp

    def test_get_cmd_strs_run(self):
        cmd = subprocess.CompletedProcess(
            args=["foo"], returncode=1, stdout=b"stdout", stderr=b"stderr"
        )
        exp = [
            "--> STDOUT",
            "stdout",
            "--> STDERR",
            "stderr",
            "--> COMMAND",
            "foo",
            "--> EXIT CODE: 1",
        ]
        data = get_cmd_strs(cmd)
        assert data == exp

    def test_get_cmd_strs_error(self):
        cmd = subprocess.CalledProcessError(
            returncode=1, cmd="foo", output=b"stdout", stderr=b"stderr"
        )
        exp = [
            "--> STDOUT",
            "stdout",
            "--> STDERR",
            "stderr",
            "--> COMMAND",
            "foo",
            "--> EXIT CODE: 1",
        ]
        data = get_cmd_strs(cmd)
        assert data == exp

    def test_get_cmd_strs_none(self):
        cmd = None
        exp = [
            "--> STDOUT",
            "",
            "--> STDERR",
            "",
            "--> COMMAND",
            "",
            "--> EXIT CODE: None",
        ]
        data = get_cmd_strs(cmd)
        assert data == exp


class TestJoinIt:
    def test_join_it_args(self):
        assert join_it("x", "y", "z") == "x y z"

    def test_join_it_list(self):
        assert join_it(["x", "y", "z"]) == "x y z"

    def test_join_it_list_joiner(self):
        assert join_it(["x", "y", "z"], joiner=", ") == "x, y, z"


class TestBytesToStr:
    def test_bytes(self):
        assert bytes_to_str(b"foo") == "foo"

    def test_bytes_ignore(self):
        assert bytes_to_str(b"foo", ignore=True) == "foo"

    def test_bytes_replace(self):
        assert bytes_to_str(b"foo", ignore=False, replace=True) == "foo"

    def test_bytes_strict(self):
        assert bytes_to_str(b"foo", ignore=False, replace=False) == "foo"

    def test_bytes_errors(self):
        assert bytes_to_str(b"foo", errors="strict") == "foo"

    def test_not_bytes(self):
        assert bytes_to_str({}) == {}


class TestStripIt:
    def test_str(self):
        assert strip_it(" foo ") == "foo"

    def test_bytes(self):
        assert strip_it(b" foo ") == b"foo"

    def test_not_str(self):
        assert strip_it(1) == 1

    def test_args(self):
        assert strip_it(" foo ", "o ") == "f"


class TestCoerceStr:
    def test_none(self):
        assert coerce_str(None) == ""

    def test_str(self):
        assert coerce_str("  foo") == "foo"

    def test_str_no_strip(self):
        assert coerce_str("  foo", strip=False) == "  foo"

    def test_bytes(self):
        assert coerce_str(b"foo") == "foo"

    def test_int(self):
        assert coerce_str(1) == "1"


class TestCoercePath:
    def test_none(self):
        assert coerce_path(None) == pathlib.Path().resolve()

    def test_str(self):
        assert coerce_path("foo") == pathlib.Path("foo").resolve()

    def test_pathlib(self):
        assert coerce_path(pathlib.Path("foo")) == pathlib.Path("foo").resolve()


class TestIsExecutable:
    def test_temp_dir(self, tmp_path):
        assert is_executable(tmp_path) is True

    def test_temp_file(self):
        with tempfile.NamedTemporaryFile() as fd:
            assert is_executable(fd.name) is False


class TestIsFile:
    def test_temp_dir(self, tmp_path):
        assert is_file(str(tmp_path)) is False

    def test_temp_file(self, tmp_path):
        path = tmp_path / "test.txt"
        path.write_text("test")
        assert is_file(str(path)) is True


class TestIsToken:
    def test_is_token(self):
        value = get_token_good()
        assert is_token(value) is True

    def test_is_token_no_length(self):
        value = get_token_bad()
        assert is_token(value, length=None) is True

    def test_is_not_token_string(self):
        value = None
        assert is_token(value) is False

    def test_is_not_token(self):
        value = get_token_bad()
        assert is_token(value) is False


class TestIsUrl:
    def test_is_url(self):
        url = get_url_good()
        assert is_url(url) is True

    def test_is_not_url_string(self):
        url = None
        assert is_url(url) is False

    def test_is_not_url(self):
        url = get_url_bad()
        assert is_url(url) is False

    def test_is_url_no_length(self):
        url = get_url_bad()
        assert is_url(url, length=None) is True


class TestEchoer:
    def test_echoer(self, caplog, capsys):
        echoer("foo")
        output = capsys.readouterr()
        assert caplog.messages == ["foo"]
        assert output.out == ""
        assert output.err == ""

    def test_echoer_echo(self, caplog, capsys):
        echoer(["foo"], echo=True)
        output = capsys.readouterr()
        assert caplog.messages == ["foo"]
        assert output.out == ""
        assert output.err == "-- foo\n"

    def test_echoer_echo_error(self, caplog, capsys):
        echoer("foo", echo=True, level="error")
        output = capsys.readouterr()
        assert caplog.messages == ["foo"]
        assert output.out == ""
        assert output.err == "!! foo\n"


class TestCheckIsFile:
    def test_is_file(self):
        assert check_is_file(value=__file__) == pathlib.Path(__file__)

    def test_is_not_file(self):
        with pytest.raises(FileNotFoundError):
            assert check_is_file(value="/foo/foo")


class TestCheckIsFileExecutable:
    def test_is_file_executable(self, tmp_path, monkeypatch):
        path = tmp_path / "foo"
        path.write_text("foo")
        monkeypatch.setattr(os, "access", lambda *args, **kwargs: True)
        assert check_is_file_executable(value=str(path)) == path

    def test_is_not_file_executable(self, tmp_path):
        path = tmp_path / "foo"
        path.write_text("foo")
        with pytest.raises(FileNotFoundError):
            check_is_file_executable(value=path)


class TestCheckIsToken:
    def test_is_token(self):
        value = get_token_good()
        assert check_is_token(value=f"  {value}  ") == value

    def test_is_not_token(self):
        with pytest.raises(ValueError):
            check_is_token(
                value=get_token_bad(),
            )

    def test_is_not_token_no_error(self):
        assert (
            check_is_token(
                value=get_token_bad(),
                error=False,
            )
            is None
        )


class TestGetPathEnv:
    def test_get_path_env_key(self, monkeypatch):
        monkeypatch.setenv("PATH", MOCK_OS_PATH)
        assert get_env_path_raw() == MOCK_OS_PATH

    def test_get_path_env(self, monkeypatch):
        monkeypatch.setenv("PATH", MOCK_OS_PATH)
        assert get_env_path() == MOCK_OS_PATH.split(os.pathsep)

    def test_get_path_env_str(self, monkeypatch):
        exp = f"{constants.PATH_HEADER}\n" + "\n".join(MOCK_OS_PATHS)
        monkeypatch.setenv("PATH", MOCK_OS_PATH)
        assert get_env_path_str() == exp


class TestArgsStr:
    def test_args_str(self):
        vittles = "foo"
        _vittles = "bar"
        _source = TestGetEnvToken
        _exp = f"{_source.__name__} with arguments:\n{constants.KEY_PREFIX}vittles: foo"
        data = args_str(source=_source, value=locals())
        assert data == _exp


class TestFindCloudflared:
    def test_defaults(self):
        data = find_cloudflared()
        assert data.is_file()
        assert is_executable(data)

    def test_executable_pathlib(self, tmp_path):
        path = tmp_path / "test_executable"
        path.touch(mode=0o755)
        data = find_cloudflared(path)
        assert data == path

    def test_executable_str(self, tmp_path):
        path = tmp_path / "test_executable"
        path.touch(mode=0o755)
        data = find_cloudflared(str(path))
        assert data == path

    def test_not_executable_pathlib(self, tmp_path):
        path = tmp_path / "test_not_executable"
        path.touch(mode=0o644)
        with pytest.raises(FileNotFoundError):
            find_cloudflared(path)

    def test_not_executable_str(self, tmp_path):
        path = tmp_path / "test_not_executable"
        path.touch(mode=0o644)
        with pytest.raises(FileNotFoundError):
            find_cloudflared(str(path))


class TestWhich:
    def test_executable_pathlib(self, tmp_path):
        path = tmp_path / "test_executable"
        path.touch(mode=0o755)
        data = which(path)
        assert data.is_file()
        assert is_executable(data)

    def test_executable_str(self, tmp_path):
        path = tmp_path / "test_executable"
        path.touch(mode=0o755)
        data = which(str(path))
        assert data.is_file()
        assert is_executable(data)

    def test_executable_bytes(self, tmp_path):
        path = tmp_path / "test_executable"
        path.touch(mode=0o755)
        data = which(str(path).encode())
        assert data.is_file()
        assert is_executable(data)


class TestPatchSubprocess:
    def test_disable_enable_disable(self):
        patch_subprocess(False)
        assert subprocess.CalledProcessError.__str__ == _called_str_original
        assert subprocess.TimeoutExpired.__str__ == _timeout_str_original

        patch_subprocess(True)
        assert subprocess.CalledProcessError.__str__ == _called_str_patched
        assert subprocess.TimeoutExpired.__str__ == _timeout_str_patched

        patch_subprocess(False)
        assert subprocess.CalledProcessError.__str__ == _called_str_original
        assert subprocess.TimeoutExpired.__str__ == _timeout_str_original


class TestListify:
    def test_list(self):
        assert listify([]) == []
        assert listify([], consume=True) == []

    def test_tuple(self):
        assert listify(()) == []
        assert listify((), consume=True) == []

    def test_set(self):
        assert listify(set()) == []
        assert listify(set(), consume=True) == []

    def test_generator_consume_false(self):
        gen = generator()
        assert listify(gen, consume=False) == gen
        assert list(gen) == [0, 1]
        assert list(gen) == []

    def test_generator_consume_true(self):
        gen = generator()
        assert listify(gen, consume=True) == [0, 1]
        assert list(gen) == []

    def test_value(self):
        assert listify(1) == [1]
        assert listify(1, consume=True) == [1]
