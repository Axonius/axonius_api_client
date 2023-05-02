"""Meta fixtures for cf_token."""
import os
import subprocess
import pathlib

from axonius_api_client.projects.cf_token import constants

MOCK_OS_PATHS = ["test1", "test2"]
MOCK_OS_PATH = os.pathsep.join(MOCK_OS_PATHS)
MOCK_ERROR_MSG = (
    "Unable to find token for provided application. Please run login command to generate token."
)
MOCK_RUN = subprocess.CompletedProcess(
    args=["foo"], returncode=1, stdout=b"stdout", stderr=b"stderr"
)
MOCK_ERROR = subprocess.CalledProcessError(
    returncode=1, cmd="foo", output=b"stdout", stderr=b"stderr"
)
MOCK_TIMEOUT = subprocess.TimeoutExpired(cmd="foo", timeout=1, output=b"stdout", stderr=b"stderr")


def patch_clear_url_envs(monkeypatch):
    """Delete any url envs."""
    for clear_key in constants.URL_ENVS:
        monkeypatch.delenv(clear_key, raising=False)


def patch_clear_token_envs(monkeypatch):
    """Delete any token envs."""
    for clear_key in constants.TOKEN_ENVS:
        monkeypatch.delenv(clear_key, raising=False)


def get_token_good():
    """Get a fake valid cloudflare access token."""
    return "a" * constants.TOKEN_LENGTH


def get_token_bad():
    """Get a fake invalid cloudflare access token."""
    return "a" * (constants.TOKEN_LENGTH - 1)


def get_url_good():
    """Get a fake valid cloudflare access url."""
    return "a" * (constants.URL_LENGTH + 1)


def get_url_bad():
    """Get a fake invalid cloudflare access url."""
    return "a" * (constants.URL_LENGTH - 1)


def patch_find_cloudflared(monkeypatch):
    """Patch find_cloudflared to return a path no matter what."""
    monkeypatch.setattr(
        "axonius_api_client.projects.cf_token.tools.find_cloudflared",
        lambda *args, **kwargs: pathlib.Path("/badwolf"),
    )


def patch_run_error(monkeypatch, exit_code=1, cmd="foo", stdout="", stderr="", module="flows"):
    """Patch run command to error."""
    exc = subprocess.CalledProcessError(returncode=exit_code, cmd=cmd, output=stdout, stderr=stderr)

    # noinspection PyUnusedLocal
    def mock_error(*args, **kwargs):
        """Mock error."""
        raise exc

    monkeypatch.setattr(
        f"axonius_api_client.projects.cf_token.{module}.run_command",
        mock_error,
    )
    return exc


def patch_run_completed(monkeypatch, cmd="foo", returncode=0, stdout="", stderr="", module="flows"):
    """Patch run_command to return completed process."""
    mock = subprocess.CompletedProcess(
        args=cmd, returncode=returncode, stdout=stdout, stderr=stderr
    )
    monkeypatch.setattr(
        f"axonius_api_client.projects.cf_token.{module}.run_command",
        lambda *args, **kwargs: mock,
    )
